import pymongo
import sys
from src.mongo.mongo_credentials import mongo_user, mongo_pass


def postMongo(body):

    connection_string = ""

    server_address = "mongodb+srv://" + mongo_user + ":" + mongo_pass + connection_string
    client = pymongo.MongoClient(server_address)
    db = client.courtbot
    mycol = db["events"]

    x = mycol.insert_many(body)
