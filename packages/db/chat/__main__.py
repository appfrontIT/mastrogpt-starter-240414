#--web true
#--kind python:default
#--annotation description "This action must be used to retrieve the chat object from the database. It will get the oldest chat and delete it until all the chat is extracted"
#--param CONNECTION_STRING $CONNECTION_STRING
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/db/chat

from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from bson.json_util import dumps
import time
import requests

def main(args):
    connection_string = args.get('CONNECTION_STRING')
    client = MongoClient(connection_string)
    dbname = client['mastrogpt']
    
    db_coll = dbname['users']
    cookie = args['__ow_headers'].get('cookie', False)
    if not cookie:
        return {"statusCode": 401}
    cookie = cookie.split("=")[1]
    user = db_coll.find_one({"cookie": cookie})
    if user:
        chat = user.get('chat', False)
        if chat and len(chat) > 0:
            db_coll.update_one({'cookie': cookie}, {"$set": {"chat": []}})
            return {"body": chat}
    return {"statusCode": 204}