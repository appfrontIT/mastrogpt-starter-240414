#--web true
#--kind python:default
#--annotation description "This action must be used to retrieve the chat object from the database. It will get the oldest chat and delete it until all the chat is extracted"

from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from bson.json_util import dumps

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
    
    db_coll = dbname['chat']

    data = db_coll.find_one()
    if data == None:
        return {"body": {"output": ""}}
    obj = format_el(data)
    db_coll.delete_one({'_id':ObjectId(data['_id'])})
    return {"body": obj}