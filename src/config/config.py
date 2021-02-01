import os
import yaml
# Write generic config file

CONFIG_DIR = os.path.expanduser("~/.courtbot-vt")
CONFIG_FILE = "config.yaml"


def generate_default_config():
    config = dict(
        calendar_root_url="https://www.vermontjudiciary.org/court-calendars",
        calendar_repo="court-calendars",
        github_branch="main",
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
    with open(os.path.join(CONFIG_DIR, CONFIG_FILE), 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    return config


def get_config_field(key):
    config = read_config()
    return config[key]


if __name__ == "__main__":
    generate_default_config()

