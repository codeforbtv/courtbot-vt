"""
Code for reading events csv, writing county-division-json files to the local court calendar repo, and comitting+pushing
the new data to the remote repo.
"""

import pandas
import json
import subprocess as cmd
import os


def create_docket_link(file_path, github_branch="main", repo_name="court-calendars", github_org="codeforbtv",
                       link_stub="https://raw.githubusercontent.com"):
    """
    Generates a github link to the raw json for a particular county_division/docket.json file
    :param file_path: string indicating path to local county_division/docket.json file
    :param repo_name: name of repo where county_division/docket.json files will be stored.
    :param github_branch: code branch in repo_name where county_division/docket.json files will be pushed.
    :param github_org: name of github organization where repo_name exists
    :param link_stub: the generic stub for raw github file content
    :return: A url in the form of:
    https://raw.githubusercontent.com/<github_org>/<repo_name>/<github_branch>/<date>/<county_division>/<docket>.json
    """
    file_sub_path = file_path.split(repo_name + "/")[1]
    docket_link = os.path.join(link_stub, github_org, repo_name, github_branch, file_sub_path)
    return docket_link


def write_events(event_csv, write_dir, local_calendar_repo, repo_name="court-calendars", github_branch="main",
                 github_org="codeforbtv", link_stub="https://raw.githubusercontent.com"):
    """
    Gather events for each unique county-division-docket combination and write json files to the court calendar github
    repo
    :param event_csv: string indicating local file path to parsed event csv
    :param write_dir: string indicating path (relative to local_calendar_repo) to directory where
    county-division-docket json files will be written
    :param local_calendar_repo: string indicating local path to court calendar repo
    :param repo_name: name of repo where county_division/docket.json files will be stored.
    :param github_branch: code branch in repo_name where county_division/docket.json files will be pushed.
    :param github_org: name of github organization where repo_name exists
    :param link_stub: the generic stub for raw github file content
    :return: A string indicating local path to lookup csv for matching county-division-docket to a github link
    containing  the raw json
    """
    calendar_table = pandas.read_csv(event_csv, dtype=str)
    lookup_table = pandas.DataFrame(dict(
        docket=calendar_table.docket,
        county=calendar_table.county,
        division=calendar_table.division,
        link=""))

    for county in list(set(calendar_table.county)):
        county = county.replace(" ", "_")

        for division in list(set(calendar_table[(calendar_table.county == county)].division)):

            court_path = os.path.join(local_calendar_repo, write_dir, county + "_" + division)
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
                link = create_docket_link(docket_path, github_branch, repo_name, github_org, link_stub)
                lookup_table.loc[
                    (calendar_table.docket == docket) &
                    (calendar_table.county == county) &
                    (calendar_table.division == division),
                    "link"] = link

    lookup_table_name = "event_lookup.csv"
    lookup_table.to_csv(os.path.join(local_calendar_repo, lookup_table_name))
    return lookup_table_name


def push_events(local_calendar_repo, events_dir):
    """
    Commit and push a folder containing new county-division-docket.json files
    :param local_calendar_repo: string indicating local path to court calendar repo
    :param events_dir: string indicating path (relative to local_calendar_repo)
    :return:
    """

    # TODO: accept github branch as an argument and potentially change to correct branch before commit/push

    os.chdir(local_calendar_repo)
    cmd.run("git add " + events_dir + "/", check=True, shell=True)
    commit_message = "'Adding newest court event json files'"
    try:
        cmd.run("git commit -m " + commit_message, check=True, shell=True)
        cmd.run("git push", check=True, shell=True)
        return True
    except cmd.CalledProcessError as e:
        print("Failed to commit and push events json files with the following error: \n" + str(e))
        return False


def push_lookup_table(local_calendar_repo, lookup_table_file):
    """
    Commit and push a the new lookup csv for matching county-division-docket to a github link
    :param local_calendar_repo: string indicating local path to court calendar repo
    :param lookup_table_file: string indicating local path (relative to local_calendar_repo) to new lookup csv
    :return:
    """

    # TODO: accept github branch as an argument and potentially change to correct branch before commit/push

    os.chdir(local_calendar_repo)
    cmd.run("git add " + lookup_table_file, check=True, shell=True)
    commit_message = "'Rewriting lookup table'"
    try:
        cmd.run("git commit -m " + commit_message, check=True, shell=True)
        cmd.run("git push", check=True, shell=True)
        return True
    except cmd.CalledProcessError as e:
        print("Failed to commit and push lookup table with the following error: \n" + str(e))
        return False


