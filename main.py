"""
This script should be run periodically to update the codeforbtv/court-calendars repo

Usage:
python3 main.py

"""
import src.parse.calendar_parse as parser
import src.github_database.write_events as event_writer
import src.mongo.write_to_mongo as write_mongo
from dotenv import load_dotenv
import os

# load config from .env file if there is one
load_dotenv()

WRITE_TO_GIT_REPO = os.getenv('WRITE_TO_GIT_REPO', 'false').lower() == 'true'
WRITE_DIR = "./data"
CALENDAR_ROOT_URL = os.getenv("CALENDAR_ROOT_URL", "https://www.vermontjudiciary.org/court-calendars")
LOCAL_CALENDAR_REPO_PATH = os.getenv("LOCAL_CALENDAR_REPO_PATH")


def main():
    """
    - Parse court calendars
    - Write json files with court events for each county-division-docket
    - Commit & push new json files and lookup csv

    :return:
    """

    print("Parsing all court calendars found at " + CALENDAR_ROOT_URL + "\n")
    events_csv, all_court_events = parser.parse_all(CALENDAR_ROOT_URL, WRITE_DIR)
    print("Finished parsing all court calendars\n")

    print("Writing court events to mongo\n")
    post_mongo = write_mongo.postMongo(all_court_events)
    print("Finished writing court events to mongo\n")

    if WRITE_TO_GIT_REPO:
        print("Writing json files for parsed court events\n")
        event_writer.write_events(events_csv, ".", LOCAL_CALENDAR_REPO_PATH)
        event_writer.commit_push(LOCAL_CALENDAR_REPO_PATH, "." + "/", "Adding newest court event json files")
        print("Finished writing json files for parsed court events\n")


if __name__ == "__main__":
    main()
