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
5. Create a `.env` file to define config variables that will be used:
```
python3 src/config/config.py
```
6. Open `.env` and populate the variables:
```
# overwrite the default path to your local court-calendar repo (created in step 2)
LOCAL_CALENDAR_REPO_PATH=/home/eugeneyum/projects/code-for-btv/court-calendars

# the connection string to use to connect to mongo
MONGODB_URI="mongodb+srv://<username>:<password>@cluster0.tcw81.mongodb.net/courtbot?retryWrites=true&w=majority"

# the mongo collection name to use in order to write the events
MONGO_COLLECTION=events

# change to true if we want to write to a local git repo
WRITE_TO_GIT_REPO=false
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
1. If `WRITE_TO_GIT_REPO=true`, make sure you set the `court-calendars` repo (cloned in step 2 of `Setup`) set to a safe development branch (i.e. not `main`).
2. Activate the virtual env (step 3 in `Setup`). 
3. Run main (parses court calendars and writes docket specific json files to the court-calendar repo):
```
python3 main.py
```
4. If `WRITE_TO_GIT_REPO=true`, check results pushed to your development branch in the `court-calendars` repo. 
5. Deactivate the virtual env (step 7 in `Setup`)

## Heroku Setup

```
# install heroku if not already
# linux
curl https://cli-assets.heroku.com/install.sh | sh

# log into heroku
heroku login

# add project to heroku
heroku git:remote -a courtbotvt-scraper

# add config vars
heroku config:set MONGODB_URI=<connection string>
heroku config:set MONGO_COLLECTION=<collection name>
```

## heroku scheduler

```
# add scheduler for daily scraping
# install scheduler addon
heroku addons:create scheduler:standard
```

go to (heroku dashboard)[https://dashboard.heroku.com/] and create a job with the following command
`python main.py`
Set it to run at 4PM UTC which is 12PM EDT or 11AM EST.

## heroku deployment

```
# deploy latest site
git push heroku main
```