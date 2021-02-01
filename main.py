import os
import datetime
import src.parse.calendar_parse as parser
import src.github_database.write_events as event_writer
import src.config.config as courtbot_config


def main():
    calendar_root_url = courtbot_config.get_config_field("calendar_root_url")
    local_calendar_repo = courtbot_config.get_config_field("local_calendar_repo_path")
    repo_name = courtbot_config.get_config_field("calendar_repo")
    github_org = courtbot_config.get_config_field("github_organization")
    github_branch = courtbot_config.get_config_field("github_branch")
    link_stub = courtbot_config.get_config_field("github_link_stub")
    today = datetime.date.today().strftime("%Y-%m-%d")
    write_dir = os.path.join(local_calendar_repo, today)
    if not os.path.isdir(write_dir):
        os.mkdir(write_dir)

    print("Parsing all court calendars found at " + calendar_root_url + "\n")
    events_csv = parser.parse_all(calendar_root_url, write_dir)
    print("Finished parsing all court calendars\n")

    print("Writing json files for parsed court events\n")
    lookup_table = event_writer.write_events(
        events_csv, write_dir, local_calendar_repo, repo_name, github_org, github_branch, link_stub)
    print("Finished writing json files for parsed court events\n")

    event_writer.push_events(local_calendar_repo, write_dir)
    event_writer.push_lookup_table(local_calendar_repo, lookup_table)


if __name__ == "__main__":
    main()


