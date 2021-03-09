"""
Code for parsing event information from Vermont Judiciary block text html calendars and writing event info to a csv.
"""

import requests
import requests_html
import datetime
import os
import re
import csv
from bs4 import BeautifulSoup

COUNTY_CODE_MAP = dict(
    an="addison",
    bn="bennington",
    ca="caledonia",
    cn="chittenden",
    ex="essex",
    fr="franklin",
    gi="grandisle",
    le="lamoille",
    oe="orange",
    os="orleans",
    rd="rutland",
    wn="washington",
    wm="windham",
    wr="windsor",
)

SUBDIV_CODE_MAP = dict(
    c="enforcement action",
    cr="criminal",
    cv="civil",
    fa="family",
    pr="probate",
    sc="small claims",
    dm="domestic",
    cs="civil suspension",
    jv="juvenile",
    mh="mental health",
    sa="TODO",  # TODO
    cm="civil miscellaneous",
)

DIVISIONS = [
    "criminal",
    "civil",
    "family",
    "probate",
    "environmental",
]


def get_court_calendar_urls(root_url):
    """
    Collect urls for individual court calendars from the Vermont Judiciary site
    :param root_url: Url to Vermont Judiciary site where all of the individual court calendars (urls) can be found.
    :return: A list of dicts containing urls to court calendars and court names:
    {
        "url": "https://www.vermontjudiciary.org/courts/court-calendars/cas_cal.htm",
        "title": "Court Calendar for Caledonia Civil Division"
    }
    """
    print("Collecting court calendar urls.\n")

    # 1) Scrape all URLS
    page = requests.get(root_url)
    data = page.text
    soup = BeautifulSoup(data, "html.parser")
    full_link_list = []
    for item in soup.find_all('a'):
        href = item.get('href')
        full_link_list.append(href)
    full_link_string = ','.join(full_link_list)

    # 2) remove itmes from list that don't start
    # "https://www.vermontjudiciary.org/courts/court-calendars"
    # TODO: This leaves out probate courts! Figure out how to incorporate these
    calendar_urls = re.findall(
        r'(https://www.vermontjudiciary.org/courts/court-calendars.+?\.htm)',
        full_link_string)
    # calendar_urls = re.findall(r'(' + ROOT_URL + r'.+?\.htm)', full_link_string)
    # 3) scrape HTML title tags from each calendar
    titles = []
    scraped_urls = []
    for calendar in calendar_urls:
        page = requests.get(calendar)
        data = page.text
        soup = BeautifulSoup(data, "html.parser")
        if soup.title is None:
            print("Could not parse '" + calendar + "'. No data found.")
            continue
        title = soup.title.string
        titles.append(title)
        scraped_urls.append(calendar)

    # 4) write dictionary with key=page title  value=full URL
    title_url_list = [{"name": title, "url": url} for title, url in zip(titles, scraped_urls)]
    print("Finished collecting court calendar urls\n")
    return title_url_list


def parse_county_subdiv_code(code):
    """
    Given a 4 letter code, use SUBDIV_CODE_MAP, and COUNTY_CODE_MAP to produce subdivision and county fields
    :param code: String of length 4. E.g. "cncr"
    :return: A tuple containing county, subvidision. E.g. (following the example above) "chittenden", "criminal"
    """
    county_code = code[:2].lower()
    subdiv_code = code[2:].lower().split('/')[0]
    county = COUNTY_CODE_MAP[county_code]
    subdiv = SUBDIV_CODE_MAP[subdiv_code]
    return county, subdiv


def parse_event_block(event_block):
    """
    Extract event information from block of formatted text
    :param event_block: A block of formatted text found within a <pre> tag in a vermont court calendar. E.g.:

    Friday,    Feb. 19                               Corporation Incorporated, LLC vs. Doe
    9:15 AM                                          114-8-20 Cacv/Civil
    Caledonia Courtroom 1                            Bench Trial
                                                     Plaintiff(s)
                                                       PCA Acquisitions V, LLC  (Jane Doe)
                                                     Defendant(s)
                                                       John Doe

    :return: A simple dictionary structured as follows:

    {
        "docket": "142-8-20",
        "county": "chittenden",
        subdivision: "criminal",
        court_room: "courtroom 1",
        hearing_type: "bench trial",
        day_of_week: "monday",
        day: "19",
        month: "february",
        time: "10:30",
        am_pm: "AM"
    }
    """
    event_text = event_block.full_text
    date_regex = r'(?P<day_of_week>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+' \
                 r'(?P<month>[a-zA-Z]{3})\.\s+(?P<day>[0-9]{1,2})'
    time_regex = r'(?P<time>[0-9]{1,2}:[0-9]{2})\s+(?P<am_pm>AM|PM)'
    docket_regex = r'(?P<docket>[0-9]{2,4}-[0-9]{1,2}-[0-9]{2})\s+(?P<category>.*$)'
    # court_room_regex = r'(?P<court_room>^.*?(?=\s{2}))'
    court_room_hearing_type_regex = r'(?P<court_room>^.*?(?=\s{2}))\s+(?P<hearing_type>.*$)'
    events = []
    dockets = set()

    lines = event_text.split('\n')
    court_room_flag = False

    day_of_week = day = month = time = am_pm = docket = category = court_room = hearing_type = ''

    for line in lines:
        if not line:
            day_of_week = day = month = time = am_pm = docket = category = court_room = hearing_type = ''
        if re.match(date_regex, line):
            group_dict = re.match(date_regex, line).groupdict()
            day_of_week = group_dict['day_of_week']
            day = group_dict['day']
            month = group_dict['month']

        if re.match(time_regex, line):
            group_dict = re.match(time_regex, line).groupdict()
            time = group_dict['time']
            am_pm = group_dict['am_pm']
            court_room_flag = True

        elif re.match(court_room_hearing_type_regex, line) and court_room_flag:
            group_dict = re.match(court_room_hearing_type_regex, line).groupdict()
            court_room = group_dict['court_room']
            hearing_type = group_dict['hearing_type']
            court_room_flag = False

        if re.search(docket_regex, line):
            group_dict = re.search(docket_regex, line).groupdict()
            docket = group_dict['docket']
            category = group_dict['category']

        if day_of_week and day and month and time and am_pm and court_room and category and docket:
            county, subdivision = parse_county_subdiv_code(category)
            if docket not in dockets:
                events.append(
                    dict(
                        docket=docket,
                        county=county,
                        subdivision=subdivision,
                        court_room=court_room,
                        hearing_type=hearing_type,
                        day_of_week=day_of_week,
                        day=day,
                        month=month,
                        time=time,
                        am_pm=am_pm
                    )
                )
                dockets.add(docket)

    return events


def parse_address(calendar):
    """
    Parse the address fields (street, city, zip) from a court calendar html response
    :param calendar: html response for an individual court calendar
    :return: A dictionary structured as follows:
    {"street": "<street name and number>", "city": "<name of city>", "zip_code": "<5 digit zip>"}
    """
    first_center_tag = calendar.html.find("center")[0]
    if len(first_center_tag.text.split('\n')) >= 3:
        address_text = first_center_tag.text.split('\n')[2]
        # TODO: what is this dot thing?
        street = address_text.split("·")[0]
        city_state_zip = address_text.split("·")[1]
        city = city_state_zip.split(",")[0]
        zip_code = city_state_zip[-5:]
    else:
        street = ""
        city = ""
        zip_code = ""

    address = dict(
        street=street,
        city=city,
        zip_code=zip_code
    )
    return address


def parse_division(court_name):
    """
    Given a court name, extract the division (one of DIVISIONS)
    :param court_name: the name of the court. e.g. "Court Calendar for Caledonia Civil Division"
    :return: A string
    """
    county_division = re.split(r"\sfor\s+", court_name)[1].lower()
    divisions = "|".join(DIVISIONS)
    division_regex = r'.*(?P<division>(' + divisions + ')).*'
    division = re.match(division_regex, county_division)
    if division:
        division = division.groupdict()['division']
    else:
        division = county_division
    return division


def parse_court_calendar(calendar, court_name):
    """
    Parse the html response for an individual court calendar into a list dicts where each dict represents an
    event.
    :param calendar: html response for an individual court calendar
    :param court_name: the name of the court. e.g. "Court Calendar for Caledonia Civil Division"
    :return: A list of dicts
    """
    events = []
    address = parse_address(calendar)
    division = parse_division(court_name)
    event_blocks = calendar.html.find('pre')
    for event_block in event_blocks:
        events = events + parse_event_block(event_block)
    [event.update(address) for event in events]
    [event.update(dict(division=division)) for event in events]
    return events


def parse_all(calendar_root_url, write_dir):
    """
    Collect all court calendar pages at calendar_root_url, parse specific events for each court calendar, and write
    all parsed events to a csv.
    :param calendar_root_url: string url where all individual court calendar html pages can be found
    :param write_dir: string indicating path to local directory where parsed event csv will be written
    :return: string indicating path to parsed event csv
    """
    if not os.path.isdir(write_dir):
        os.mkdir(write_dir)

    date = datetime.date.today().strftime("%Y-%m-%d")
    court_cals = get_court_calendar_urls(calendar_root_url)
    all_court_events = []
    for court_cal in court_cals:
        session = requests_html.HTMLSession()
        court_url = court_cal['url']
        court_name = court_cal['name']
        print("Begin parsing '" + court_name + "' at '" + court_url + "'.")
        response = session.get(court_url)
        if response.ok:
            court_events = parse_court_calendar(response, court_name)
        else:
            print("ERROR: " + response.status_code + "\n")
            continue
        if not len(court_events):
            print("No data found for " + court_name + " at " + court_url + "\n")
            continue
        else:
            all_court_events = all_court_events + court_events
            print("Done parsing '" + court_name + "' at '" + court_url + "'.\n")

    keys = all_court_events[0].keys()
    write_file = os.path.join(write_dir,  'court_events.csv')
    with open(write_file, 'w') as wf:
        dict_writer = csv.DictWriter(wf, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_court_events)

    return write_file
