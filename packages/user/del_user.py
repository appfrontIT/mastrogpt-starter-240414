#--web true
#--kind python:default

import requests
import json

def main(args):
    print(args)
    data = {"delete": True, "filter": {"id": args.get('id')}}
    response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"collection": "users", "data": data})
    if response.status_code == 200:
        obj = response.json()
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/action/del_package", json={"name": obj['name']})
    return {"name": response['name']}