import os
import pandas
import datetime
import json
import re
import src.config.config as courtbot_config

repo_name = courtbot_config.get_config_field("calendar_repo")
github_org = courtbot_config.get_config_field("github_organization")
local_calendar_repo = courtbot_config.get_config_field("local_calendar_repo_path")
link_stub = courtbot_config.get_config_field("github_link_stub")


def create_docket_link(file_path, github_branch="main"):
    file_sub_path = file_path.split(repo_name + "/")[1]
    docket_link = os.path.join(link_stub, github_org, repo_name, github_branch, file_sub_path)
    return docket_link


# TODO: 1) get today's calendar
today = datetime.date.today().strftime("%Y-%m-%d")
calendar_table = pandas.read_csv(os.path.join(local_calendar_repo, today, "court_events_" + today + ".csv"), dtype=str)
lookup_table = pandas.DataFrame(dict(
    docket=calendar_table.docket,
    county=calendar_table.county,
    division=calendar_table.division,
    link=""))

# TODO: 2) get dockets for each county/division and write events
for county in list(set(calendar_table.county)):
    county = county.replace(" ", "_")

    for division in list(set(calendar_table[(calendar_table.county == county)].division)):

        court_path = os.path.join(local_calendar_repo, today, county + "_" + division)
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
            link = create_docket_link(docket_path, github_branch="lj_2020-12-22")  # TODO: drop this special branch
            lookup_table.loc[
                (calendar_table.docket == docket) &
                (calendar_table.county == county) &
                (calendar_table.division == division),
                "link"] = link

lookup_table.to_csv(os.path.join(local_calendar_repo, today, "lookup_" + today + ".csv"))
