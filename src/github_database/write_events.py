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


def commit_push(repo_directory, add_path, message):
    """

    :param repo_directory: string indicating local path to court calendar repo
    :param add_path: string indicating path (relative to repo_directory) of file(s) to add, commit, and push
    :param message: string commit message
    :return: True if successful, False if errors were encountered
    """
    # TODO: accept github branch as an argument and potentially change to correct branch before commit/push

    os.chdir(repo_directory)
    cmd.run("git add" + add_path, check=True, shell=True)
    try:
        cmd.run("git commit -m '" + message + "'", check=True, shell=True)
        cmd.run("git push", check=True, shell=True)
        return True
    except cmd.CalledProcessError as e:
        print("Failed to commit and push with the following error: \n" + str(e))
        return False




