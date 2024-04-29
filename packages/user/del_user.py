#--web true
#--kind python:default
#--annotation description 'an action which delete an user to the database. Required parameters: {'id': id}'

import requests
import json

def main(args):
    data = {"filter": {"_id": args.get('_id')}}
    user = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json= {
        "find_by_id": True,
        "collection": "users",
        "data": {"filter": args.get('_id')}
        })
    response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={
        "delete": True,
        "collection": "users",
        "data": data
        })
    if response.status_code == 200:
        obj = user.json()
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/package/del_package", json={"name": obj['name']})
    return {"name": response.text}