import subprocess as cmd
import datetime
import os
import src.config.config as courtbot_config

local_calendar_repo = courtbot_config.get_config_field("local_calendar_repo_path")
today = datetime.date.today().strftime("%Y-%m-%d")

os.chdir(local_calendar_repo)
cmd.run("git add " + today + "/", check=True, shell=True)
commit_message = "'Adding court event json files for " + today + "'"
cmd.run("git commit -m " + commit_message, check=True, shell=True)

# TODO: Shouldn't need to '--set-upstream' down the road...
# cmd.run("git push --set-upstream origin lj_2020-12-22", check=True, shell=True)

cmd.run("git push", check=True, shell=True)

