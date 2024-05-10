#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"

import requests
import hashlib

def create(args):
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
    package = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/default/package/create", json={"name": username})
    if package.status_code == 200:
        response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/add", json={"data": data})
        if response.status_code == 200:
            return {"body": response.text}
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/default/package/delete", json={"name": username})
        return {"statusCode": response.status_code, "body": "Failed creating the user"}
    return {"statusCode": package.status_code, "body": package.text}

def delete(args):
    id = args.get('id', False)
    if not id:
        return {"statusCode": 400}
    user = requests.get(f'https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?id={id}')
    if user.status_code == 404:
        return {"statusCode": 404}
    response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/delete?id=" + id)
    if response.status_code == 400:
        return {"statusCode": response.status_code, "body": response.text}
    if user.status_code == 200:
        obj = user.json()
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/default/package/delete", json={"name": obj['package']})
        return {"statusCode": 204}
    return {"statusCode": response.status_code}

def update(args):
    # print(args)
    data = args.get('data', False)
    id = args.get('id', False)
    if not data or not id:
        return {"statusCode": 400}
    response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/update?id=" + id, json={"data": data})
    if response.status_code == 400:
        return {"statusCode": response.status_code, "body": response.text}
    if response.status_code == 200:
        return {"statusCode": response.status_code, "body": response.text}
    return {"statusCode": response.status_code}

def find(args):
    cookie = args.get('cookie', False)
    if not cookie:
        return {"statusCode": 400}
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?cookie={cookie}")
    if response.status_code != 404:
        return {"statusCode": 200, "body": response.text}
    return {"statusCode": 404}
    

def main(args):
    path = args.get('__ow_path', False)
    if not path:
        return {"statusCode": 500}
    if path == '/create':
        if args['__ow_method'] != 'post':
            return {"statusCode": 405}
        return create(args)
    elif path == '/delete':
        if args['__ow_method'] != 'delete':
            return {"statusCode": 405}
        return delete(args)
    elif path == '/update':
        if args['__ow_method'] != 'put':
            return {"statusCode": 405}
        return update(args)
    elif path == '/find':
        if args['__ow_method'] != 'get':
            return {"statusCode": 405}
        return find(args)
    return {"statusCode": 400}