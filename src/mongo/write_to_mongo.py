import os
from pymongo import InsertOne, UpdateOne, MongoClient
from dotenv import load_dotenv
import logging
import json
from datetime import date, datetime

# load config from .env file if there is one
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "events")

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def updateOperation(event):
    """
    Converts an event into a mongodb bulk write operation

    :param event: event document to inserted to mongo
    :return: mongodb operation
    """
    return UpdateOne({ "_id": event["_id"] }, { "$set": event }, upsert=True)

def combineEvents(events):
    """
    Goes thru all the collected events and combines multiple case dates into 1 event document

    :param events: list of scraped events
    :return: unique list of events with dates combined if multiple events with the same docket #
    """
    eventsMap = {}

    for event in events:
        uid = f"{event['county']}_{event['subdivision']}_{event['docket']}"

        # check to see if uid exists in dict
        if uid in eventsMap:
            # add date to array
            eventsMap[uid]["date"].append(event["date"])
        else:
            # add unique id
            event["_id"] = uid
            # convert date to an array
            event["date"] = [event["date"]]
            eventsMap[uid] = event

    uniqueEvents = list(eventsMap.values())
    return uniqueEvents


def postMongo(events):
    """
    gets a list of scraped events, does some processing and saves them to mongo

    :param events: list of scraped events
    """
    # throw an error if the mongo connection string is not set
    if MONGODB_URI is None:
        raise Exception("MONGODB_URI environment variable is not set")

    client = MongoClient(MONGODB_URI)
    db = client.courtbot
    mycol = db[MONGO_COLLECTION]

    uniqueEvents = combineEvents(events)

    operations = list(map(updateOperation, uniqueEvents))

    mycol.bulk_write(operations)
