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
    reset = args.get('reset_history', False)
    id = args.get('id', False)
    if not id:
        return {"statusCode": 400}
    client = MongoClient(connection_string)
    dbname = client['mastrogpt']
    collection = dbname['users']
    if reset:
        collection.update_one({'_id': ObjectId(id)}, {"$unset": {"chat": 1, "history": 1}})
    message = args.get('message', False)
    history = args.get('history', False)
    if message and history:
        # message['output'] = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/formatter', json={"input": message['output']}).text
        collection.update_one({'_id': ObjectId(id)}, {"$addToSet": {"chat": message, "history": history}})
    elif message and not history:
        # message['output'] = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/formatter', json={"input": message['output']}).text
        collection.update_one({'_id': ObjectId(id)}, {"$addToSet": {"chat": message}})
    elif history and not message:
        collection.update_one({'_id': ObjectId(id)}, {"$addToSet": {"history": history}})
    return {"statusCode": 204}