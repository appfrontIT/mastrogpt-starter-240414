#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action append a message to the user chat"

from pymongo import MongoClient
import os

def main(args):
    print(args)
    reset = args.get('reset_history', False)
    cookie = args.get('cookie', False)
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mastrogpt']
    collection = dbname['users']
    if not cookie:
        return {"statusCode": 400}
    if reset:
        collection.update_one({'cookie': cookie}, {"$unset": {"chat": 1, "history": 1}})
    message = args.get('message', False)
    history = args.get('history', False)
    collection.update_one({'cookie': cookie}, {"$addToSet": {"chat": message, "history": history}})
    return {"statusCode": 204}