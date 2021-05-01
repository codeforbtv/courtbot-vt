"""
Html text parsing tests
"""
import src.parse.calendar_parse as parser
from bs4 import BeautifulSoup


def test_parse_address():
    address_text = """Court Calendar for
    Addison Criminal Division
    7 Mahady Court · Middlebury, VT 05753
    (802) 388-4237
    """
    expected_result = dict(
        street="7 mahady court",
        city="middlebury",
        zip_code="05753"
    )
    assert parser.parse_address(address_text) == expected_result


def test_parse_division():
    division_text = "Court Calendar for Addison Criminal Division"
    expected_result = "criminal"
    assert parser.parse_division(division_text) == expected_result


def test_county_subdiv_code():
    code_text = "Ancr"
    expected_result = "addison", "criminal"
    assert parser.parse_county_subdiv_code(code_text) == expected_result


def test_parse_date():
    date_text = "Monday,    Mar. 29                               State vs. Fitzgerald, Erica"
    expected_result = "monday", "29", "mar"
    assert parser.parse_date(date_text) == expected_result

    date_text = "Tuesday,   May   4                               Estate of James D. Michelson, vs. Gilmore"
    expected_result = "tuesday", "4", "may"
    assert parser.parse_date(date_text) == expected_result


def test_parse_time():
    time_text = "9:00 AM                                          199-6-19 Ancr/Criminal"
    expected_result = "9:00", "am"
    assert parser.parse_time(time_text) == expected_result


def test_parse_court_details():
    court_details_text = "Superior Court Courtroom 1                       Change of Plea Hearing"
    expected_result = "superior court courtroom 1", "change of plea hearing"
    assert parser.parse_court_details(court_details_text) == expected_result


def test_parse_docket_category():
    docket_category_text = "9:00 AM                                          199-6-19 Ancr/Criminal"
    expected_result = "199-6-19", "ancr/criminal"
    assert parser.parse_docket_category(docket_category_text) == expected_result


def test_parse_event_block():
    event_block_text = """
Date/Time/Place                                  Case Name/Type of Proceeding/Litigants (Attorney)
--------------------------------------------------------------------------------------------------
Monday,    Mar. 29                               State vs. Woodward, Taylor
9:00 AM                                          199-6-19 Ancr/Criminal
Superior Court Courtroom 1                       Change of Plea Hearing
                                                 Plaintiff, State of Vermont  (Peter M. Bevere)
                                                 Defendant, Taylor Woodward  (James Arthur Gratton)
Monday,    Mar. 29                               State vs. Fitzgerald, Erica
9:00 AM                                          289-8-19 Ancr/Criminal
Superior Court Courtroom 1                       Change of Plea Hearing
                                                 Plaintiff, State of Vermont  (Peter M. Bevere)
                                                 Defendant, Erica Fitzgerald  (James Arthur Gratton)
                                                 Victim's Advocate, Deb James (Victim Advocate)
Monday,    Mar. 29                               State vs. Fitzgerald, Erica
9:00 AM                                          43-1-20 Ancr/Criminal
Superior Court Courtroom 1                       Change of Plea Hearing
                                                 Plaintiff, State of Vermont  (Dennis M. Wygmans)
                                                 Defendant, Erica Fitzgerald  (James Arthur Gratton)
"""
    expected_result = [
        dict(
            docket="199-6-19",
            county="addison",
            subdivision="criminal",
            court_room="superior court courtroom 1",
            hearing_type="change of plea hearing",
            day_of_week="monday",
            day="29",
            month="mar",
            time="9:00",
            am_pm="am"
        ),
        dict(
            docket="289-8-19",
            county="addison",
            subdivision="criminal",
            court_room="superior court courtroom 1",
            hearing_type="change of plea hearing",
            day_of_week="monday",
            day="29",
            month="mar",
            time="9:00",
            am_pm="am"
        ),
        dict(
            docket="43-1-20",
            county="addison",
            subdivision="criminal",
            court_room="superior court courtroom 1",
            hearing_type="change of plea hearing",
            day_of_week="monday",
            day="29",
            month="mar",
            time="9:00",
            am_pm="am"
        )
    ]
    assert expected_result == parser.parse_event_block(event_block_text)


def test_get_court_events():
    event_1 = dict(
        docket="73-7-20",
        county="lamoille",
        subdivision="civil",
        division="civil",
        court_room="lamoille superior courtroom #1",
        hearing_type="eviction hearing",
        day_of_week="tuesday",
        day="4",
        month="may",
        time="9:00",
        am_pm="am",
        street="po box 570",
        city="hyde park",
        zip_code="05655"
    )

    event_2 = dict(
        docket="73-7-20",
        county="lamoille",
        subdivision="civil",
        division="civil",
        court_room="lamoille superior courtroom #1",
        hearing_type="eviction hearing",
        day_of_week="wednesday",
        day="5",
        month="may",
        time="9:00",
        am_pm="am",
        street="po box 570",
        city="hyde park",
        zip_code="05655"
    )

    with open("tests/test_calendar.txt", "r") as test_calendar:
        response_text = test_calendar.read()

    soup = BeautifulSoup(response_text, "html.parser")

    assert [event_1, event_2] == parser.get_court_events(soup, soup.title.get_text())
