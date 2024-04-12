#--web true
#--kind python:default

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
            "updateData": {
                "role": args.get("role")
            }
    }
    response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"collection": "users", "data": data})
    return {"body": response.text}