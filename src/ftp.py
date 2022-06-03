"""
This script should be run daily to get csv data from ftp server

Usage:
python3 ftp.py

"""
import base64
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
import pysftp


logging.basicConfig(level=logging.INFO)

# load config from .env file if there is one
load_dotenv()

SFTP_HOST = os.getenv("SFTP_HOST", "gs.judiciary.vermont.gov")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USERNAME = os.getenv("SFTP_USERNAME", None)
SFTP_PRIVATE_KEY_BASE64 = os.getenv("SFTP_PRIVATE_KEY_BASE64", None)
MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "events")

def updateOperation(event):
    """
    Converts an event into a mongodb bulk write operation

    :param event: event document to inserted to mongo
    :return: mongodb operation
    """
    return UpdateOne({ "_id": event["_id"] }, { "$set": event }, upsert=True)

def ftp():
    if MONGODB_URI is None:
        raise Exception("MONGODB_URI environment variable is not set")

    # get csv from ftp server
    logging.info("Downloading file from sftp server")
    try:
        # Use 'io.StringIO' to read your string as a file-like object.
        decoded_private_key=base64.b64decode(SFTP_PRIVATE_KEY_BASE64).decode('utf-8')
        privkey = io.StringIO(decoded_private_key)

        logging.info(str(privkey))

        # Use paramiko to create your RSAKey
        ki = paramiko.RSAKey.from_private_key(privkey)

        # connect to sftp
        conn = pysftp.Connection(host=SFTP_HOST,port=SFTP_PORT,username=SFTP_USERNAME, private_key=ki)
        logging.info("connection established successfully")
    except Exception as e:
        logging.error(e)
        exit(1)
    current_dir = conn.pwd
    logging.info('our current working directory is: ',current_dir)
    files = conn.listdir()
    logging.info('available list of files: ', files)

    # # read in xlsx as panda
    # logging.info('reading excel file as panda')
    # df = pd.read_excel("./data/sample.xlsx", header=None)

    # # panda to object
    # logging.info('converting panda to json objects')
    # events = []
    # for index, row in df.iterrows():
    #     event = {
    #         "_id": f"{row[1]} {row[3]} {row[10]}",
    #         "date": datetime.strptime(f"{row[2]} {row[5]}", '%m/%d/%Y %H:%M').replace(tzinfo=dateutil.tz.gettz('America/New_York')),
    #         "county": {
    #             "code": row[1],
    #             "name": row[24],
    #         },
    #         "division": row[3],
    #         "judge": {
    #             "code": row[4],
    #             "name": row[28],
    #         },
    #         "court_room_code": row[7],
    #         "hearing": {
    #             "date": row[2],
    #             "start_time": row[5],
    #             "type_code": row[8],
    #             "type": row[25],
    #         },
    #         "doc_id": row[9],
    #         "docket_number": row[10],
    #         "case": {
    #             "name": row[11],
    #             "status": row[27],
    #             "type": row[26],
    #         },
    #         "litigant": {
    #             "entity_id": row[12],
    #             "last_name": row[13],
    #             "first_name": row[14],
    #             "full_name": row[15],
    #             "role": {
    #                 "code": row[16],
    #                 "rank": row[17],
    #                 "description": row[29],
    #             },
    #             "number": row[18],
    #         },
    #         "attorney": {
    #             "entity_id": row[19],
    #             "last_name": row[20],
    #             "first_name": row[21],
    #             "suffix": row[22],
    #             "full_name": row[23],
    #         },
    #         "calendar_id": row[30],
    #     }
    #     events.append(event)

    # # write to mongo
    # logging.info('writing to mongo')
    # client = MongoClient(MONGODB_URI)
    # db = client.courtbot
    # mycol = db[MONGO_COLLECTION]
    # operations = list(map(updateOperation, events))
    # mycol.bulk_write(operations)

if __name__ == "__main__":
    ftp()
