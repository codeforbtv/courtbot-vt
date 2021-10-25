import os
from pymongo import InsertOne, UpdateOne, MongoClient
from dotenv import load_dotenv
import logging

# load config from .env file if there is one
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "events")

def updateOperation(event):
    # event["_id"] = f"{event['county']}_{event['subdivision']}_{event['docket']}"
    # return UpdateOne({ "_id": event["_id"] }, { "$set": event }, upsert=True)
    return InsertOne(event)

def postMongo(body):
    # throw an error if the mongo connection string is not set
    if MONGODB_URI is None:
        raise Exception("MONGODB_URI environment variable is not set")

    client = MongoClient(MONGODB_URI)
    db = client.courtbot
    mycol = db[MONGO_COLLECTION]

    operations = list(map(updateOperation, body))

    # mycol.bulk_write(operations)
