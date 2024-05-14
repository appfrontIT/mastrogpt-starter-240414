#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action retrieve the user history"
#--param CONNECTION_STRING $CONNECTION_STRING

from pymongo import MongoClient
from bson.objectid import ObjectId
import os

def main(args):
    connection_string = args.get('CONNECTION_STRING', False)
    client = MongoClient(connection_string)
    dbname = client['mastrogpt']
    collection = dbname['users']
    id = args.get('id', False)
    if not id:
        return {"statusCode": 400}
    data = collection.find_one({'_id': ObjectId(id)})
    return {"statusCode": 200, "body": data['history']}