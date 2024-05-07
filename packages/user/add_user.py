#--web true
#--kind python:default
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"

import requests
import hashlib

def main(args):
    name = args.get('name', False)
    password = args.get('password', False)
    role = args.get('role', False)
    if not name or not password or not role:
        return {"statusCode": 400}
    if role == "admin":
        package = 'default'
    else:
        package = name
    data = {
        "name": name,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": role,
        "namespace": f"gporchia/{package}",
        "package": package,
        "shared package": [],
        "chat": [],
    }
    package = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/package/add_package", json={"name": name})
    if package.status_code == 200:
        response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "collection": "users", "data": data})
        if response.status_code == 200:
            return {"body": response.text}
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/package/del_package", json={"name": name})
        return {"statusCode": 500, "body": "Failed creating the user, please try again"}
    return {"statusCode": 500, "body": "Failed creating the package, please try again"}