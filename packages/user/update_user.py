#--web true
#--kind python:default
#--annotation description 'an action which update an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}'

import requests
import json
import hashlib

def main(args):
    data = {
        "update": True,
            "filter": {
                "name": args.get('name'),
                "password": hashlib.sha256(args.get("password").encode()).hexdigest(),
            },
            "updateData": args.get('updateData')
    }
    response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"update": True, "collection": "users", "data": data})
    return {"body": response.text}