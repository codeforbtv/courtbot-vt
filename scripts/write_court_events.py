import os
import pandas
import datetime
import json

calendar_repo_root = os.path.expanduser("~/Code/lib/code4btv/court-calendars")

# TODO: 1) get today's calendar
today = datetime.date.today().strftime("%Y-%m-%d")
calendar_table = pandas.read_csv(os.path.join(calendar_repo_root, today, "court_events_" + today + ".csv"))

# TODO: 2) get dockets for each county/division and write events
for county in list(set(calendar_table.county)):
    county = county.replace(" ", "_")

    for division in list(set(calendar_table[(calendar_table.county == county)].court_type)):
        division = division.split(" ")[0].lower()

        court_path = os.path.join(calendar_repo_root, today, county + "_" + division)
        # Make court folder if it doesn't exist
        if not os.path.isdir(court_path):
            os.mkdir(court_path)

        docket_groups = calendar_table[
            (calendar_table.county == county) & (calendar_table.division == division)].groupby("docket")

        for docket in docket_groups.groups.keys():
            print("County: " + county + " Division: " + division + " Docket: " + docket + "\n")
            docket_events = docket_groups.get_group(docket).to_dict("records")
            docket_path = os.path.join(court_path, docket + ".json")
            with open(docket_path, "w") as docket_file:
                json.dump(docket_events, docket_file)
