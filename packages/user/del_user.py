#--web true
#--kind python:default

import requests
import json

def main(args):
    data = {"delete": True, "filter": {"_id": args.get('id')}}
    response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"collection": "users", "data": data})
    return {"body": response.text}