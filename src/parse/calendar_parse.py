import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date


def parse_event_block(case_text: str, date: datetime) -> dict:
    """Parse an event block from a court .htm page.

    Args:
        case_text (str): text for a specific case/event block
        date (datetime): date that this event happens

    Returns:
        dict: dictionary of something like
        {
            "docket": "142-8-20",
            "county": "chittenden",
            subdivision: "criminal",
            court_room: "courtroom 1",
            hearing_type: "bench trial",
            date: isoformat datetime
        }
    """
    splits = case_text.lower().splitlines()
    clean_splits = [split.strip() for split in splits]
    cleaner_splits = [split for split in clean_splits if split and '----' not in split]
    bad_line = bool([split for split in cleaner_splits if splits if split.endswith('v.') and 'vs.' not in split])

    if not bad_line:
        time_and_subdivision = cleaner_splits[1].split('   ')
        clean_time = time_and_subdivision[0]
        time_splits = clean_time[:-3].split(':')
        hour = int(time_splits[0])
        if clean_time.endswith('pm'):
            hour += 12  # 24 hr time here...
        minute = int(time_splits[1])

        maybe_dirty_docket, subdivision = time_and_subdivision[-1].lstrip().split('/')
        dockets = [maybe_dirty_docket.split(' ')[0]]  # clean 3926-11-18 cncr

        court_room_and_hearing_type = cleaner_splits[2].split('   ')
        court_room = court_room_and_hearing_type[0]
        hearing_type = court_room_and_hearing_type[-1]

    else:
        time_and_hearing_type = cleaner_splits[0].split('   ')
        clean_time = time_and_hearing_type[0]
        time_splits = clean_time[:-3].split(':')
        hour = int(time_splits[0])
        if clean_time.endswith('pm'):
            hour += 12  # 24 hr time here...
        minute = int(time_splits[1])
        hearing_type = time_and_hearing_type[-1].lstrip()

        court_room = cleaner_splits[1].split('   ')[0]
        dockets = []
        for cleaner_split in cleaner_splits[2:]:
            dockets.append(cleaner_split.split('/')[-1])

        subdivision = None

    full_date = datetime(date.year, date.month, date.day, hour, minute)

    return {
        'docket': dockets,
        'subdivision': subdivision,
        'court_room': court_room,
        'hearing_type': hearing_type,
        'date': full_date.isoformat()
    }


def parse_courtroom_from_day(courtroom_text: str, date: datetime) -> list:
    """Parse an entire day's worth of cases/events from a single courtroom.

    Args:
        courtroom_text (str): text for an entire day
        date (datetime): date of the day

    Returns:
        list: list of event dicts that parse_event_block returns
    """
    judge = courtroom_text.splitlines()[0].rstrip()[1:]
    week_fit_len = 11
    weekday = date.strftime("%A,")
    weekday_whitespace = ' ' * (week_fit_len - len(weekday))
    day_whitespace = ' '
    month = date.strftime("%b.")
    day = date.strftime("%-d")
    split_str = f"{weekday}{weekday_whitespace}{month}{day_whitespace}{day}"
    cases_text = courtroom_text.split(split_str)[1:]

    event_blocks = []
    for case_text in cases_text:
        event_blocks.append(parse_event_block(case_text, date))

    return event_blocks


def parse_day(day_text: str, date: datetime) -> list:
    """Parse an entire day's worth of cases/events, may be multiple rooms.

    Args:
        day_text (str): text for that entire day
        date (datetime): date of day

    Returns:
        list: list of event dicts that parse_event_block returns
    """
    splits = day_text.split('Cases heard by')[1:]
    for split in splits:
        event_blocks = parse_courtroom_from_day(split, date)

    return event_blocks


def parse_date(day_text: str) -> datetime:
    """Parse the month and day out of a day text.

    Args:
        day_text (str): text for that entire day

    Returns:
        datetime: _description_
    """
    date = day_text.splitlines()[0]
    month_day = date[date.index(', ') + 2:]

    # clean month
    month = month_day[:4].replace(' ', '')
    month = datetime.strptime(month, "%b").month

    dirty_day = month_day[4:]
    # get day number out
    day = ""
    for ch in dirty_day:
        if ch.isdigit():
            day += (ch)
    day = int(day)

    today = datetime.today()
    date = datetime(year=today.year, month=month, day=day)

    return date


def parse_calendar(calendar_link: str) -> list:
    """Parse an entire calendar for a given court page.

    Args:
        calendar_link (str): link to .htm page

    Returns:
        list: list of event blocks dicts from parse_event_block
    """
    text = requests.get(calendar_link).text
    no_html = re.sub('<[^<]+?>', '', text)
    cases_text = no_html[no_html.index('As of'):]
    days_text = cases_text.split('Cases Set for  ')[1:]

    event_blocks = []
    for day_text in days_text:
        date = parse_date(day_text)
        event_blocks += parse_day(day_text, date)

    return event_blocks


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
    url_string = ','.join(urls)
    # remove items from list that don't start
    # "https://www.vermontjudiciary.org/courts/court-calendars"
    # TODO: This leaves out probate courts! Figure out how to incorporate these

    filtered_urls = re.findall(
        r'(https://www.vermontjudiciary.org/courts/court-calendars.+?\.htm)',
        url_string
    )
    return filtered_urls


def parse_all(calendar_root_url: str) -> list:
    """Parse all court events for a given tree of case pages.

    Args:
        calendar_root_url (str): root url of all pages

    Returns:
        list: list of event blocks dicts from parse_event_block
    """
    # TODO: need to add county back into the court events dict, should be quick as the below variable is all flat
    logging.info("Beginning to collect court calendar urls.")
    landing_page = requests.get(calendar_root_url)
    if not landing_page.ok:
        raise(requests.HTTPError("Failed to calendar root url: " + calendar_root_url))
    landing_soup = BeautifulSoup(landing_page.text, "html.parser")
    court_urls = extract_urls_from_soup(landing_soup)
    court_urls = filter_bad_urls(court_urls)
    logging.info("Finished collecting court calendar urls")

    all_court_events = []
    for court_url in court_urls:
        all_court_events += parse_calendar(court_url)

    return all_court_events
