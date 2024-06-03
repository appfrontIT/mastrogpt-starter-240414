#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action append a message to the user chat"
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation url https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message

from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import requests

def main(args):
    connection_string = args.get('CONNECTION_STRING', False)
    id = args.get('id', False)
    if not id:
        return {"statusCode": 400}
    client = MongoClient(connection_string)
    dbname = client['mastrogpt']
    collection = dbname['users']
    message = args.get('message', False)
    if message:
        collection.update_one({'_id': ObjectId(id)}, {"$addToSet": {"chat": message}})
    return {"statusCode": 204}