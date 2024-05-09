#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"

import requests
import hashlib

def main(args):
    username = args.get('username', False)
    password = args.get('password', False)
    role = args.get('role', False)
    if not username or not password or not role:
        return {"statusCode": 400}
    if role == "admin":
        package = 'default'
    else:
        package = username
    data = {
        "username": username,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": role,
        "namespace": f"gporchia/{package}",
        "package": package,
        "shared package": [],
        "chat": [],
    }
    package = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/package/add", json={"name": username})
    if package.status_code == 200:
        response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "collection": "users", "data": data})
        if response.status_code == 200:
            return {"body": response.text}
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/package/del", json={"name": username})
        return {"statusCode": response.status_code, "body": "Failed creating the user"}
    return {"statusCode": package.status_code, "body": package.text}