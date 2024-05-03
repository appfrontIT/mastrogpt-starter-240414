#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action retrieve the user history"

from pymongo import MongoClient
import os

def main(args):
    cookie = args.get('cookie', False)
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mastrogpt']
    collection = dbname['users']
    if not cookie:
        return {"statusCode": 400}
    data = collection.find_one({'cookie': cookie})
    return {"statusCode": 200, "body": data['history']}