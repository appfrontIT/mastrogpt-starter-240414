#--web true
#--kind python:default
#--annotation description "This action returns the function to load on the editor"
#--param CONNECTION_STRING $CONNECTION_STRING
#--timeout 300000

from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import requests
import time

def main(args):
    headers = args['__ow_headers']
    cookie = headers.get('cookie', False)
    if not cookie:
        return {'statusCode': 404}
    cookie = cookie.split("=")[1]
    connection_string = args.get('CONNECTION_STRING', False)
    client = MongoClient(connection_string)
    dbname = client['mastrogpt']
    collection = dbname['users']

    path = args.get('__ow_path', False)
    if path == '/get':
        loop_time = 0
        function = None
        while True:
            user = collection.find_one({"cookie": cookie})
            if user:
                editor = user.get('editor', False)
            if editor and len(editor) > 0:
                break
            elif loop_time > 20:
                return {"statusCode": 204}
            time.sleep(5)
            loop_time += 5
        collection.update_one({'cookie': cookie}, {"$set": {"editor": None}})
        return {"statusCode": 200, "body": editor}
    elif path == '/add':
        collection.update_one({'cookie': cookie}, {'$set': {'editor': args.get('editor', 'error')}})
        return {'statusCode': 204}
    return {'statusCode': 404}