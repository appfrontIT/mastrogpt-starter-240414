#--web true
#--kind python:default
#--annotation description 'an action which find an user to the database. Required parameters: {'name': name, 'password': password} or {'id': id}'

import requests
import hashlib

def main(args):
    cookie = args.get('cookie', '')
    data = {
        "find_one": True,
        "filter": {
            "cookie": cookie,
        }
    }
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find_one": True, "collection": "users", "data": data})
    if response.status_code != 404:
        return {"body": response.text}
    else:
        return {"statusCode": 404}