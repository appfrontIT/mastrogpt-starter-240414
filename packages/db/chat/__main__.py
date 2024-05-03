#--web true
#--kind python:default
#--annotation description "This action must be used to retrieve the chat object from the database. It will get the oldest chat and delete it until all the chat is extracted"
#--timeout 600000

from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from bson.json_util import dumps
import time

def format_el(element):
    ret = {}
    for key in element:
        if key != '_id':
            ret[key] = element[key]
    return ret

def main(args):
    # connection_string = args.get('CONNECTION_STRING')
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mastrogpt']
    
    db_coll = dbname['users']
    cookie = args['__ow_headers'].get('cookie', False)
    if not cookie:
        return {"statusCode": 401}
    cookie = cookie.split("=")[1]
    loop_time = 0
    data = None
    while True:
        data = db_coll.find_one({"cookie": cookie}, {'chat': 1, '_id': 0})
        if data and data != None:
            break
        elif loop_time > 20:
            return {"statusCode": 204}
        time.sleep(2)
        loop_time += 2
    obj = format_el(data)
    db_coll.update_one({'cookie': cookie}, {"$unset": {"chat": 1}})
    return {"body": obj}