"""
This script should be run daily to get csv data from ftp server

Usage:
python3 ftp.py

"""
from datetime import datetime
import dateutil.tz
from dotenv import load_dotenv
import io
import json
import logging
import os
import pandas as pd
import paramiko
from pymongo import InsertOne, UpdateOne, MongoClient


logging.basicConfig(level=logging.INFO)

# load config from .env file if there is one
load_dotenv()

SFTP_HOST = os.getenv("SFTP_HOST", "gs.judiciary.vermont.gov")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USERNAME = os.getenv("SFTP_USERNAME", None)
SFTP_PRIVATE_KEY = os.getenv("SFTP_PRIVATE_KEY", None)
MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "events")
CLEAR_FTP_SERVER = os.getenv("CLEAR_FTP_SERVER", "false").lower() == 'true'

def updateOperation(event):
    """
    Converts an event into a mongodb bulk write operation

    :param event: event document to inserted to mongo
    :return: mongodb operation
    """
    return UpdateOne({ "_id": event["_id"] }, { "$set": event }, upsert=True)

def read_file_to_panda(path):
    return pd.read_excel(path, header=None)


def get_uid(event):
    return f"{event['county']['code']}-{event['division']}-{event['docket_number']}-{event['litigant']['entity_id']}-{event['litigant']['role']['code']}"

def csv_to_event(row):
    event = {
        "date": datetime.strptime(f"{row[2]} {row[5]}", '%m/%d/%Y %H:%M').replace(tzinfo=dateutil.tz.gettz('America/New_York')),
        "county": {
            "code": row[1],
            "name": row[24],
        },
        "division": row[3],
        "judge": {
            "code": row[4],
            "name": row[28],
        },
        "court_room_code": row[7],
        "hearing": {
            "date": row[2],
            "start_time": row[5],
            "type_code": row[8],
            "type": row[25],
        },
        "doc_id": row[9],
        "docket_number": row[10],
        "case": {
            "name": row[11],
            "status": row[27],
            "type": row[26],
        },
        "litigant": {
            "entity_id": row[12],
            "last_name": row[13],
            "first_name": row[14],
            "full_name": row[15],
            "role": {
                "code": row[16],
                "rank": row[17],
                "description": row[29],
            },
            "number": row[18],
        },
        "attorney": {
            "entity_id": row[19],
            "last_name": row[20],
            "first_name": row[21],
            "suffix": row[22],
            "full_name": row[23],
        },
        "calendar_id": row[30],
    }
    event['_id'] = get_uid(event)
    return event

def ftp():
    if MONGODB_URI is None:
        raise Exception("MONGODB_URI environment variable is not set")

    # get csv from ftp server
    try:
        logging.info("Connecting to sftp server")
        # create ssh client
        ssh = paramiko.SSHClient()
        # auto add host to host key list
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        # set private key from env variable
        key = paramiko.RSAKey.from_private_key(io.StringIO(SFTP_PRIVATE_KEY.replace('\\n', '\n')))
        # connect with ssh and disabling some pubkey algorithms in order to use 'ssh-rsa' algorithm
        ssh.connect(SFTP_HOST, port=SFTP_PORT, username=SFTP_USERNAME, pkey=key, disabled_algorithms=dict(pubkeys=['rsa-sha2-256', 'rsa-sha2-512']))
        # open sftp
        with ssh.open_sftp() as sftp:
            # list the files
            files = sftp.listdir()

            # assume the last file listed is the latest file
            if (len(files) == 0):
                logging.info("No new files found on ftp server")
                exit(0)
            latest_file = files[-1]

            # create tmp directory if it doesn't exist
            if not os.path.exists('./tmp'):
                os.makedirs('./tmp')
            logging.info(f"downloading file from sftp server: {latest_file}")
            sftp.get(latest_file, f"./tmp/{latest_file}")

            # read in xlsx as panda
            logging.info('reading excel file as panda')
            df = read_file_to_panda(f"./tmp/{latest_file}")

            # panda to event object
            logging.info('converting panda to json objects')
            events = []
            for index, row in df.iterrows():
                events.append(csv_to_event(row))
            logging.info(f'read in {len(events)} events')

            # removing duplicate events
            logging.info('removing duplicate events')
            events_to_write = unique_events(events)
            logging.info(f'number of unique events: {len(events_to_write)}')

            # write to mongo
            logging.info('writing to mongo')
            client = MongoClient(MONGODB_URI)
            db = client.courtbot
            mycol = db[MONGO_COLLECTION]
            operations = list(map(updateOperation, events_to_write))
            mycol.bulk_write(operations)

            # remove all files
            if CLEAR_FTP_SERVER:
                logging.info('removing ftp files')
                for file in files:
                    logging.info(f"removing {file}")
                #     sftp.remove(file)
    except Exception as e:
        logging.error(e)
        exit(1)

def unique_events(events):
    # initialize a null list
    unique_ids = []
    unique_events = []
    # traverse for all elements
    for o in events:
        # check if exists in unique_list or not
        if o['_id'] not in unique_ids:
            unique_ids.append(o['_id'])
            unique_events.append(o)
    return unique_events

if __name__ == "__main__":
    ftp()
