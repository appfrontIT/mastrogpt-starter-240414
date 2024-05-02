#--web true
#--kind python:default

import requests
from pymongo import MongoClient
from pymongo import errors
from bson.objectid import ObjectId
import json

def main(args):
    cookie = args['__ow_headers'].get('cookie', False)
    user = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/user/find_by_cookie", headers={"Content-Type": "application/json"}, json={
        "cookie": cookie
        })
    if user.status_code != 404:
        user_obj = user.json()
        print(user_obj['ID'])
        update = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo', json={
            "update": True,
            "collection": "users",
            "data": {
                "filter": {"_id": user_obj['ID']},
                "updateData": {"cookie": None}
            }
        })
    return {"statusCode": 200, "body": {"logout": True, "cookie": cookie.split('=')[0]}}