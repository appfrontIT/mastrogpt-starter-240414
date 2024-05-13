#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"
#--param JWT_SECRET $JWT_SECRET

import requests
import hashlib
import jwt

def create(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    decoded = jwt.decode(token, key=secret, algorithms='HS256')
    if decoded['role'] != 'admin':
        return {'statusCode': 401}
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
        "shared_package": [],
        "chat": [],
    }
    package = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/default/package/create", json={"name": username})
    if package.status_code == 200:
        response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/add", json={"data": data})
        if response.status_code == 200:
            return {"statusCode": 200, "body": response.json()}
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/default/package/delete", json={"name": username})
        return {"statusCode": response.status_code, "body": "Failed creating the user"}
    return {"statusCode": package.status_code, "body": package.text}

def delete(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    decoded = jwt.decode(token, key=secret, algorithms='HS256')
    if decoded['role'] != 'admin':
        return {'statusCode': 401}
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
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    decoded = jwt.decode(token, key=secret, algorithms='HS256')
    if decoded['role'] != 'admin':
        return {'statusCode': 401}
    data = args.get('data', False)
    id = args.get('id', False)
    if not data or not id:
        return {"statusCode": 400}
    response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/update?id=" + id, json={"data": data})
    if response.status_code == 200:
        return {"statusCode": response.status_code, "body": response.text}
    return {"statusCode": response.status_code}

def find(args):
    id = args.get('id', False)
    if not id:
        return {"statusCode": 400}
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?id={id}")
    if response.status_code != 404:
        return {"statusCode": 200, "body": response.text}
    return {"statusCode": 404}
    

def main(args):
    path = args['__ow_path']
    if path == '/add' and args['__ow_method'] != 'post':
        return create(args)
    elif path == '/delete' and args['__ow_method'] != 'delete':
        return delete(args)
    elif path == '/update' and args['__ow_method'] != 'put':
        return update(args)
    elif path == '/find'and args['__ow_method'] != 'get':
        return find(args)
    return {"statusCode": 404}