# courtbot-vt

Python code to grab xlsx file of all court events provided on sftp server and write them to Mongo.

Project Lead: Stephen Chisa

Tech Lead: Lucas Johnson

## Setup
1. Clone the courtbot-vt repo:
```
git clone git@github.com:codeforbtv/courtbot-vt.git
```
2. In the courtbot-vt folder create a virtual environment and activate it:
```
python3 -m venv env
source env/bin/activate
```
3. Install packages inside the virtual environment:
```
pip install -r requirements.txt
```
4. Create a `.env` file to define config variables that will be used in `src/ftp.py`
5. Open `.env` and populate the variables:
```
SFTP_HOST
SFTP_PORT
SFTP_USERNAME
SFTP_PRIVATE_KEY
MONGODB_URI
MONGO_COLLECTION
CLEAR_FTP_SERVER
```

## To Deactivate virtual env

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
1. Activate the virtual env (step 3 in `Setup`). 
2. Run ftp
```
python3 src/ftp.py
```

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
heroku config:set SFTP_HOST=<host name>
```

## heroku scheduler

```
# add scheduler for daily scraping
# install scheduler addon
heroku addons:create scheduler:standard
```

go to (heroku dashboard)[https://dashboard.heroku.com/] and create a job with the following command
`python src/ftp.py`
Set it to run at 4PM UTC which is 12PM EDT or 11AM EST.

## heroku deployment

```
# deploy latest site
git push heroku main
```
