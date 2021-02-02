# courtbot-vt
Python code to scrape [Vermont court calendars](https://www.vermontjudiciary.org/court-calendars) and populate our
cache of [calendar data](https://github.com/codeforbtv/court-calendars).

Project Lead: Stephen Chisa

Tech Lead: Lucas Johnson

## Setup and Run
1. Clone the courtbot-vt repo:
```
git clone git@github.com:codeforbtv/courtbot-vt.git
```
2. Clone the court-calendars repo:
```
git clone git@github.com:codeforbtv/court-calendars.git
```
3. In the courtbot-vt folder create a virtual environment and activate it:
```
python3 -m venv env
source env/bin/activate
```
4. Install packages inside the virtual environment:
```
pip install -r requirements.txt
```
5. Generate a yaml config file (writes a file to `~/.courtbot-vt/config.yaml`):
```
python3 src/config/config.py
```
6. Open `~/.courtbot-vt/config.yaml` and overwrite the default path to your local court-calendar repo
(created in step 2):
```
local_calendar_repo_path: <path_to_court-calendar_repo>
```
7. Potentially overwrite the default github branch for the court-calendar repo `~/.courtbot-vt/config.yaml` file:
```
github_branch: <branch_where_new_events_will_be_pushed>
```
8. Run main (parses court calendars and writes docket specific json files to the court-calendar repo):
```
python3 main.py
```
9. Deactivate the virtual env
```
deactivate
```

