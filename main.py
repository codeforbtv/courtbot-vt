"""
This script should be run periodically to update the codeforbtv/court-calendars repo

Usage:
python3 main.py

"""
import src.parse.calendar_parse as parser
import src.github_database.write_events as event_writer
import src.config.config as courtbot_config


def main():
    """
    - Parse court calendars
    - Write json files with court events for each county-division-docket
    - Commit & push new json files and lookup csv

    :return:
    """
    calendar_root_url = courtbot_config.get_config_field("calendar_root_url")
    local_calendar_repo = courtbot_config.get_config_field("local_calendar_repo_path")

    print("Parsing all court calendars found at " + calendar_root_url + "\n")
    events_csv = parser.parse_all(calendar_root_url, local_calendar_repo)
    print("Finished parsing all court calendars\n")

    print("Writing json files for parsed court events\n")
    event_writer.write_events(events_csv, ".", local_calendar_repo)
    print("Finished writing json files for parsed court events\n")

    event_writer.commit_push(local_calendar_repo, "." + "/", "Adding newest court event json files")


if __name__ == "__main__":
    main()
