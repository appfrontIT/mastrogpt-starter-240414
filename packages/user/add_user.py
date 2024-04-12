#--web true
#--kind python:default

import requests
import hashlib

def main(args):
    data = {
        "name": args.get("name"),
        "password": hashlib.sha256(args.get("password").encode()).hexdigest(),
        "role": args.get("role")
    }
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"collection": "users", "data": data})
    return {"body": response.text}