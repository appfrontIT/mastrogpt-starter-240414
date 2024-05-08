#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action append a message to the user chat"

from pymongo import MongoClient
import os
import requests

def main(args):
    reset = args.get('reset_history', False)
    cookie = args.get('cookie', False)
    if not cookie:
        return {"statusCode": 400}
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mastrogpt']
    collection = dbname['users']
    if reset:
        collection.update_one({'cookie': cookie}, {"$unset": {"chat": 1, "history": 1}})
    message = args.get('message', False)
    history = args.get('history', False)
    if message and history:
        message['output'] = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/formatter', json={"input": message['output']}).text
        collection.update_one({'cookie': cookie}, {"$addToSet": {"chat": message, "history": history}})
    elif message and not history:
        message['output'] = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/formatter', json={"input": message['output']}).text
        collection.update_one({'cookie': cookie}, {"$addToSet": {"chat": message}})
    elif history and not message:
        collection.update_one({'cookie': cookie}, {"$addToSet": {"history": history}})
    return {"statusCode": 204}