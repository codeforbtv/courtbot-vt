"""
Code for parsing event information from Vermont Judiciary block text html calendars and writing event info to a csv.
"""

import requests
import os
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime

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
    fg='fish and game',
    ta='traffic appeal'
)

DIVISIONS = [
    "criminal",
    "civil",
    "family",
    "probate",
    "environmental",
]


def extract_urls_from_soup(soup):
    """
    Extract a list of urls from a BeautifulSoup object
    :param soup: a BeautifulSoup object
    :return: a list of urls (strings)
    """
    urls = []
    for item in soup.find_all('a'):
        href = item.get('href')
        urls.append(href)
    return urls


def filter_bad_urls(urls):
    """
    Remove urls that we can't parse (yet)
    :param urls: list of urls (strings)
    :return: filtered list of urls (strings)
    """
    url_string = ','.join(urls)

    # remove items from list that don't start
    # "https://www.vermontjudiciary.org/courts/court-calendars"
    # TODO: This leaves out probate courts! Figure out how to incorporate these

    filtered_urls = re.findall(
        r'(https://www.vermontjudiciary.org/courts/court-calendars.+?\.htm)',
        url_string
    )
    return filtered_urls


def parse_county_subdiv_code(code):
    """
    Given a 4 letter code, use SUBDIV_CODE_MAP, and COUNTY_CODE_MAP to produce subdivision and county fields
    :param code: String of length 4. E.g. "cncr"
    :return: A tuple containing county, subvidision. E.g. (following the example above) "chittenden", "criminal"
    """
    if code is None:
        return "", ""
    else:
        county_code = code[:2].lower()
        subdiv_code = code[2:].lower().split('/')[0]
        county = COUNTY_CODE_MAP[county_code]
        subdiv = SUBDIV_CODE_MAP[subdiv_code]
        return county.strip().lower(), subdiv.strip().lower()


def parse_date(line):
    """
    Extract the day of week, day, and month from a line of text
    :param line: string
    :return: dayofweek, day, month
    """
    date_regex = r'(?P<day_of_week>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+' \
                 r'(?P<month>[a-zA-Z]{3})\.?\s+(?P<day>[0-9]{1,2})'

    if re.match(date_regex, line):
        group_dict = re.match(date_regex, line).groupdict()
        day_of_week = group_dict['day_of_week']
        day = group_dict['day']
        month = group_dict['month']
        return day_of_week.strip().lower(), day.strip().lower(), month.strip().lower()
    else:
        return "", "", None


def parse_time(line):
    """
    Extract time and am/pm from a line of text
    :param line: string
    :return: time, am/pm
    """
    time_regex = r'(?P<time>[0-9]{1,2}:[0-9]{2})\s+(?P<am_pm>AM|PM)'
    if re.match(time_regex, line):
        group_dict = re.match(time_regex, line).groupdict()
        time = group_dict['time']
        am_pm = group_dict['am_pm']
        return time.strip().lower(), am_pm.strip().lower()
    else:
        return "", ""


def parse_court_details(line):
    """
    Extract courtroom and hearing type from a line of text
    :param line: string
    :return: courtroom, hearing type
    """
    court_room_hearing_type_regex = r'(?P<court_room>^.*?(?=\s{2}))\s+(?P<hearing_type>.*$)'
    if re.match(court_room_hearing_type_regex, line):
        group_dict = re.match(court_room_hearing_type_regex, line).groupdict()
        court_room = group_dict['court_room']
        hearing_type = group_dict['hearing_type']
        return court_room.strip().lower(), hearing_type.strip().lower()
    else:
        return "", ""


def parse_docket_category(line):
    """
    Extract docket and category code from a line of text
    :param line: string
    :return: docket, category code
    """
    docket_regex = r'(?P<docket>[0-9]{2,4}-[0-9]{1,2}-[0-9]{2})\s+(?P<category>.*$)'
    if re.search(docket_regex, line):
        group_dict = re.search(docket_regex, line).groupdict()
        docket = group_dict['docket']
        category = group_dict['category']
        return docket.strip().lower(), category.strip().lower()
    else:
        return "", ""

def get_date_time(day,month,time,am_pm):

    month_int = int(datetime.strptime(month, '%b').strftime('%m'))
    now = datetime.now()
    now_month = now.month
    now_year = now.year
    if month_int <= now_month-6:
            year = now_year+1
    else: year = now_year
    date_time_str = day + "/" + month + "/" + str(year) + " " + time + am_pm #but we will need to check we need the actual year or year +1
    date_time_obj = datetime.strptime(date_time_str, '%d/%b/%Y %I:%M%p')

    return date_time_obj


def parse_event_block(event_text):
    """
    Extract event information from block of formatted text
    :param event_text: A block of formatted text found within a <pre> tag in a vermont court calendar. E.g.:

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
    events = []
    lines = event_text.split('\n')
    court_room_flag = False

    day_of_week = day = month = time = am_pm = docket = category = court_room = hearing_type = ''
    for line in lines:
        print(line)
        if not line:
            day_of_week = day = month = time = am_pm = docket = category = court_room = hearing_type = ''
            continue
        if not day_of_week and not day and not month:
            day_of_week, day, month = parse_date(line)

        if not time and not am_pm:
            time, am_pm = parse_time(line)
            if time and am_pm:
                court_room_flag = True
        elif time and am_pm and court_room_flag:
            court_room, hearing_type = parse_court_details(line)
            if court_room and hearing_type:
                court_room_flag = False

        if not docket and not category:
            docket, category = parse_docket_category(line)

        if day_of_week and day and month and time and am_pm and court_room and category and docket:
            county, subdivision = parse_county_subdiv_code(category)

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
                    am_pm=am_pm,
                    date = get_date_time(day,month,time,am_pm)
                )
            )
            day_of_week = day = month = time = am_pm = docket = category = court_room = hearing_type = ''


    return events


def parse_address(address_text):
    """
    Parse the address fields (street, city, zip) from a court calendar html response
    :param address_text: text containing address information
    :return: A dictionary structured as follows:
    {"street": "<street name and number>", "city": "<name of city>", "zip_code": "<5 digit zip>"}
    """

    if len(address_text.split('\n')) >= 3:
        address_text = address_text.split('\n')[2]
        # TODO: what is this dot thing?
        street = address_text.split("·")[0]
        city_state_zip = address_text.split("·")[1]
        city = city_state_zip.split(",")[0]
        zip_code = city_state_zip[-6:]
    else:
        street = ""
        city = ""
        zip_code = ""

    address = dict(
        street=street.strip().lower(),
        city=city.strip().lower(),
        zip_code=zip_code.strip()
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


def get_court_events(calendar_soup, court_name):
    """
    Parse the html response for an individual court calendar into a list dicts where each dict represents an
    event.
    :param calendar_soup: BeautifulSoup object containing calendar html
    :param court_name: the name of the court. e.g. "Court Calendar for Caledonia Civil Division"
    :return: A list of dicts
    """
    events = []
    address = parse_address(calendar_soup.find("center").get_text().strip())
    division = parse_division(court_name)
    event_blocks = calendar_soup.findAll('pre')
    for event_block in event_blocks:
        events = events + parse_event_block(event_block.get_text().strip())
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

    print("Beginning to collect court calendar urls.\n")
    landing_page = requests.get(calendar_root_url)
    if not landing_page.ok:
        raise(requests.HTTPError("Failed to calendar root url: " + calendar_root_url))
    landing_soup = BeautifulSoup(landing_page.text, "html.parser")
    court_urls = extract_urls_from_soup(landing_soup)
    court_urls = filter_bad_urls(court_urls)
    print("Finished collecting court calendar urls\n")

    all_court_events = []
    for court_url in court_urls:
        print("Begin parsing court calendar at '" + court_url + "'.")
        response = requests.get(court_url)
        if response.ok:
            calendar_soup = BeautifulSoup(response.text, "html.parser")
            court_name = calendar_soup.title.get_text()
            court_events = get_court_events(calendar_soup, court_name)
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

    return write_file, all_court_events
