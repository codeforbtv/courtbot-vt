"""
This script should be run daily to get csv data from ftp server

Usage:
python3 ftp.py

"""
import json
from dotenv import load_dotenv
import logging
import os
import pandas as pd
import pysftp

logging.basicConfig(level=logging.INFO)

# load config from .env file if there is one
load_dotenv()

SFTP_HOST = os.getenv("SFTP_HOST", "gs.judiciary.vermont.gov")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USERNAME = os.getenv("SFTP_USERNAME", None)
SFTP_PASSWORD = os.getenv("SFTP_PASSWORD", None)

def ftp():
    # get csv from ftp server
    # logging.info("Downloading file from sftp server")
    # try:
    #     conn = pysftp.Connection(host=SFTP_HOST,port=SFTP_PORT,username=SFTP_USERNAME, password=SFTP_PASSWORD)
    #     logging.info("connection established successfully")
    # except Exception as e:
    #     logging.error(e)
    #     exit(1)
    # current_dir = conn.pwd
    # logging.info('our current working directory is: ',current_dir)
    # files = conn.listdir()
    # logging.info('available list of files: ', files)

    # read in xlsx as panda
    df = pd.read_excel("./data/sample.xlsx", header=None)

    # panda to object
    events = []
    for index, row in df.iterrows():
        event = {
            "id": f"{row[1]} {row[3]} {row[10]}",
            "date": f"{row[2]} {row[5]}",
            "county_code": row[1],
            "hearing_date": row[2],
            "division": row[3],
            "judge_code": row[4],
            "start_time": row[5],
            "court_room_code": row[7],
            "hearing_type_code": row[8],
            "doc_id": row[9],
            "docket_number": row[10],
            "case_name": row[11],
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
            "county_name": row[24],
            "hearing_type": row[25],
            "case_type": row[26],
            "case_status": row[27],
            "judge_name": row[28],
            "calendar_id": row[30],
        }
        events.append(event)

    # write to mongo

if __name__ == "__main__":
    ftp()
