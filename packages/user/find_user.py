#--web true
#--kind python:default

import requests
import hashlib

def main(args):
    password = args.get('password', '')
    if password != '':
        password = hashlib.sha256(password.encode()).hexdigest()
    data = {
        "find_one": True,
        "filter": {
            "name": args.get('name'),
            "password": password,
            "_id": args.get('id', '')
        }
    }
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"collection": "users", "data": data})
    return {"body": response.text}