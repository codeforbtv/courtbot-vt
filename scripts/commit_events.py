import subprocess as cmd
import datetime
import os

calendar_repo_root = os.path.expanduser("~/Code/lib/code4btv/court-calendars")
today = datetime.date.today().strftime("%Y-%m-%d")

os.chdir(calendar_repo_root)
cmd.run("git add " + today + "/", check=True, shell=True)
commit_message = "'Adding court event json files for " + today + "'"
cmd.run("git commit -m " + commit_message, check=True, shell=True)

# TODO: Shouldn't need to '--set-upstream' down the road...
cmd.run("git push --set-upstream origin lj_2020-12-22", check=True, shell=True)



