"""
Provides functions to lookup fields in the config. Also serves as a script for generating a default configuration file
for a new setup/install.

Usage (creates and writes a default config file at ~/.courtbot-vt/config.yaml):
python3 config.py
"""

import os
import yaml

CONFIG_DIR = os.path.expanduser("~/.courtbot-vt")
CONFIG_FILE = "config.yaml"


def generate_default_config():
    """
    Generate a default yaml config file. Should be run once for a new setup/install or when additional config fields
    are added
    :return:
    """
    config = dict(
        calendar_root_url="https://www.vermontjudiciary.org/court-calendars",
        calendar_repo="court-calendars",
        github_branch="dev",
        github_organization="codeforbtv",
        github_link_stub="https://raw.githubusercontent.com",
    )
    local_calendar_repo_path = os.path.expanduser(
        os.path.join(
            "~",
            config['github_organization'],
            config['calendar_repo']
        )
    )
    config.update(
        dict(
            local_calendar_repo_path=local_calendar_repo_path
        )
    )
    if not os.path.isdir(CONFIG_DIR):
        os.mkdir(CONFIG_DIR)

    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), 'w') as config_file:
        yaml.dump(config, config_file)


# Get config file contents
def read_config():
    """
    Read the user specific config file from disk and return the contents as a simple dictionary
    :return: A dictionary containing config fields and values
    """
    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    return config


def get_config_field(key):
    """
    Retrieve a value from the config by looking up '`ey`
    :param key: A string to lookup a value in the config
    :return: A value from the config
    """
    config = read_config()
    return config[key]


if __name__ == "__main__":
    generate_default_config()

