"""
This script should be run daily to get csv data from ftp server

Usage:
python3 ftp.py

"""
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
    dfs = pd.read_excel("./data/sample.xlsx")
    dfs.to_csv("./data/sample.csv", sep=",")

    # panda to object

    # write to mongo

if __name__ == "__main__":
    ftp()
