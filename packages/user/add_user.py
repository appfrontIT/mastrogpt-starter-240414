#--web true
#--kind python:default
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"

import requests
import hashlib

def main(args):
    data = {
        "name": args.get("name"),
        "password": hashlib.sha256(args.get("password").encode()).hexdigest(),
        "role": args.get("role")
    }
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "collection": "users", "data": data})
    if response.status_code == 200:
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/action/add_package", json={"name": args.get("name")})
    return {"body": response.text}