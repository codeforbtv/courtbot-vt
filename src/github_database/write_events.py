import pandas
import json
import subprocess as cmd
import os


def create_docket_link(file_path, github_branch, github_org, repo_name, link_stub):
    file_sub_path = file_path.split(repo_name + "/")[1]
    docket_link = os.path.join(link_stub, github_org, repo_name, github_branch, file_sub_path)
    return docket_link


def write_events(event_csv, write_dir, local_calendar_repo, repo_name, github_org, github_branch, link_stub):

    calendar_table = pandas.read_csv(event_csv, dtype=str)
    lookup_table = pandas.DataFrame(dict(
        docket=calendar_table.docket,
        county=calendar_table.county,
        division=calendar_table.division,
        link=""))

    for county in list(set(calendar_table.county)):
        county = county.replace(" ", "_")

        for division in list(set(calendar_table[(calendar_table.county == county)].division)):

            court_path = os.path.join(write_dir, county + "_" + division)
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
                link = create_docket_link(docket_path, github_branch, github_org, repo_name, link_stub)
                lookup_table.loc[
                    (calendar_table.docket == docket) &
                    (calendar_table.county == county) &
                    (calendar_table.division == division),
                    "link"] = link

    lookup_table_name = "event_lookup.csv"
    lookup_table.to_csv(os.path.join(local_calendar_repo, lookup_table_name))
    return lookup_table_name


def push_events(local_calendar_repo, events_dir):
    # TODO: accept github branch as an argument and potentially change to correct branch before commit/push

    os.chdir(local_calendar_repo)
    cmd.run("git add " + events_dir + "/", check=True, shell=True)
    commit_message = "'Adding newest court event json files'"
    cmd.run("git commit -m " + commit_message, check=True, shell=True)
    cmd.run("git push", check=True, shell=True)


def push_lookup_table(local_calendar_repo, lookup_table_file):
    # TODO: accept github branch as an argument and potentially change to correct branch before commit/push

    os.chdir(local_calendar_repo)
    cmd.run("git add " + lookup_table_file, check=True, shell=True)
    commit_message = "'Rewriting lookup table'"
    cmd.run("git commit -m " + commit_message, check=True, shell=True)
    cmd.run("git push", check=True, shell=True)

