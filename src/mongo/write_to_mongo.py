import os
import pymongo
from dotenv import load_dotenv

# load config from .env file if there is one
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "events")

def postMongo(body):
    # throw an error if the mongo connection string is not set
    if MONGODB_URI is None:
        raise Exception("MONGODB_URI environment variable is not set")

    client = pymongo.MongoClient(MONGODB_URI)
    db = client.courtbot
    mycol = db[MONGO_COLLECTION]

    x = mycol.insert_many(body)
