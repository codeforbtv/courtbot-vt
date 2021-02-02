"""
This script should be run periodically to update the codeforbtv/court-calendars repo

Usage:
python3 main.py

"""
import os
import datetime
import src.parse.calendar_parse as parser
import src.github_database.write_events as event_writer
import src.config.config as courtbot_config


def main():
    """
    - Parse court calendars
    - Write json files with court events for each county-division-docket
    - Write a lookup csv
    - Commit & push new json files and lookup csv

    :return:
    """
    calendar_root_url = courtbot_config.get_config_field("calendar_root_url")
    local_calendar_repo = courtbot_config.get_config_field("local_calendar_repo_path")
    repo_name = courtbot_config.get_config_field("calendar_repo")
    github_org = courtbot_config.get_config_field("github_organization")
    github_branch = courtbot_config.get_config_field("github_branch")
    link_stub = courtbot_config.get_config_field("github_link_stub")
    today = datetime.date.today().strftime("%Y-%m-%d")

    print("Parsing all court calendars found at " + calendar_root_url + "\n")
    events_csv = parser.parse_all(calendar_root_url, os.path.join(local_calendar_repo, today))
    print("Finished parsing all court calendars\n")

    print("Writing json files for parsed court events\n")
    lookup_table = event_writer.write_events(events_csv, today, local_calendar_repo, repo_name, github_branch,
                                             github_org, link_stub)
    print("Finished writing json files for parsed court events\n")

    event_writer.commit_push(local_calendar_repo, today + "/", "Adding newest court event json files")
    event_writer.commit_push(local_calendar_repo, os.path.basename(lookup_table),  "Rewriting lookup table")


if __name__ == "__main__":
    main()


