# courtbot-vt
Python code to scrape [Vermont court calendars](https://www.vermontjudiciary.org/court-calendars) and populate our
cache of [calendar data](https://github.com/codeforbtv/court-calendars).

Project Lead: Stephen Chisa

Tech Lead: Lucas Johnson

## Setup
1. Clone the courtbot-vt repo:
```
git clone https://github.com/codeforbtv/courtbot-vt.git
```
2. Clone the court-calendars repo:
```
https://github.com/codeforbtv/court-calendars.git
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
7. Deactivate the virtual env
```
deactivate
```

## Tests
1. Activate the virtual env (step 3 in `Setup`)
2. Run the tests:
```
pytest
```
3. Deactivate the virtual env when you are finished (step 7 in `Setup`). 

## Run
1. Make sure you set the `court-calendars` repo (cloned in step 2 of `Setup`) set to a safe development branch (i.e. not `main`). 
2. Overwrite the default github branch for the court-calendar repo in the `~/.courtbot-vt/config.yaml` file (generated in step 5 of `Setup`). This branch name should match the branch you set/created in step 1 of `Run`.:
```
github_branch: <branch_where_new_events_will_be_pushed>
```
3. Activate the virtual env (step 3 in `Setup`). 
4. Run main (parses court calendars and writes docket specific json files to the court-calendar repo):
```
python3 main.py
```
5. Check results pushed to your development branch in the `court-calendars` repo. 
6. Deactivate the virtual env (step 7 in `Setup`)
