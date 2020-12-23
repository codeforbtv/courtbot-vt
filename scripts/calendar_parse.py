import requests
import requests_html
import datetime
import sys
import os
import re
import csv
from bs4 import BeautifulSoup

ROOT_URL = "https://www.vermontjudiciary.org/court-calendars"

COUNTY_CODE_MAP = dict(
    an="addison",
    bn="bennington",
    ca="caledonia",
    cn="chittenden",
    ex="essex",
    fr="franklin",
    gi="grand isle",
    le="lamoille",
    oe="orange",
    os="orleans",
    rd="rutland",
    wn="washington",
    wm="windham",
    wr="windsor",
)

DIV_CODE_MAP = dict(
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


def get_court_calendar_urls(root_url):
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
    calendar_urls = re.findall(r'(https://www.vermontjudiciary.org/courts/court-calendars.+?\.htm)', full_link_string)

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


def parse_county_div_code(code):
    county_code = code[:2].lower()
    div_code = code[2:].lower().split('/')[0]
    county = COUNTY_CODE_MAP[county_code]
    div = DIV_CODE_MAP[div_code]
    return county, div


def parse_event_block(event_block):
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
            county, division = parse_county_div_code(category)
            if docket not in dockets:
                events.append(
                    dict(
                        docket=docket,
                        county=county,
                        division=division,
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
    first_center_tag = calendar.html.find("center")[0]
    if len(first_center_tag.text.split('\n')) >= 3:
        address_text = first_center_tag.text.split('\n')[2]
        # TODO: what is this dot thing?
        street = address_text.split("·")[0]
        city_state_zip = address_text.split("·")[1]
        city = city_state_zip.split(",")[0]
        zip_code = city_state_zip[-6:]
        print(zip_code)
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


def parse_court_type(court_name):
    county_division = re.split(r"\sfor\s+", court_name)[1]
    if len(re.split(r"\s+", county_division)) == 3:
        court_type = re.split(r"\s+", county_division)[1] + " " + re.split(r"\s+", county_division)[2]
    else:
        court_type = county_division
    return court_type


def parse_court_calendar(calendar, court_name):
    events = []
    address = parse_address(calendar)
    court_type = parse_court_type(court_name)
    event_blocks = calendar.html.find('pre')
    for event_block in event_blocks:
        events = events + parse_event_block(event_block)
    [event.update(address) for event in events]
    [event.update(dict(court_type=court_type)) for event in events]
    return events


def main(argv):

    write_dir = argv[0]
    date = datetime.date.today().strftime("%Y-%m-%d")
    court_cals = get_court_calendar_urls(ROOT_URL)
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
    write_file = os.path.join(write_dir,  'court_events_' + date + ".csv")
    with open(write_file, 'w') as wf:
        dict_writer = csv.DictWriter(wf, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_court_events)


if __name__ == "__main__":
    main(sys.argv[1:])
    # main(["/tmp/output.csv"])