#--web true
#--kind python:default

import requests
from pymongo import MongoClient
from pymongo import errors
from bson.objectid import ObjectId
import json

def main(args):
    cookie = args['__ow_headers'].get('cookie', False)
    if not cookie:
        return {"statusCode": 400}
    cookie_spl = cookie.split('=')
    user = requests.get(f'https://nuvolaris.dev/api/v1/web/gporchia/default/user/find?cookie={cookie_spl[1]}')
    if user.status_code != 404:
        user_obj = user.json()
        update = requests.put('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/update?id='+user_obj['_id'], json={
                "data": {"cookie": None}
        })
    return {"statusCode": 200, "body": {"logout": True, "cookie": cookie_spl[0]}}