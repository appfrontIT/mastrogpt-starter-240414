#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"
#--param JWT_SECRET $JWT_SECRET
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/base/user

import requests
import hashlib
import jwt
import json
import urllib
import secrets

def get_pendings(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    decoded = jwt.decode(token, key=secret, algorithms='HS256')
    if decoded['role'] != 'admin' and decoded['role'] != 'root':
        return {'statusCode': 401}
    response = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/signup/find_many", headers={'Authorization': 'Bearer ' + token})
    if response.status_code != 404:
        return {"statusCode": 200, "body": response.json()}
    return {"statusCode": 404}
    
    
def create(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    decoded = jwt.decode(token, key=secret, algorithms='HS256')
    if decoded['role'] != 'admin' and decoded['role'] != 'root':
        return {'statusCode': 401}
    name = args.get('name', '')
    surname = args.get('surname', '')
    username = args.get('username', None)
    email = args.get('email', '')
    role = args.get('role', None)
    if not username or not role:
        return {"statusCode": 400}
    if role != 'user' and role != 'admin':
        return {'statusCode': 400, 'body': 'role invalid. Must be one of: user, admin'}
    response = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'username': username})),
                        headers={"Authorization": "Bearer " + token})
    if response.status_code == 200:
        return {"statusCode": 400, "body": {"error": "username unavailable"}}
    openapi = f"""{{
        "openapi": "3.1.0",
        "info": {{
            "title": "{username} - OpenAPI 3.1",
    "termsOfService": "http://swagger.io/terms/",
    "version": "1.0.11"
    }},
    "servers": [{{"url": "https://walkiria.cloud/api/v1/web"}}],
    "components": {{
    "securitySchemes": {{
        "bearerAuth": {{
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
            }}
        }}
    }},
    "paths": {{}}
    }}"""
    package = [username]
    password = secrets.token_urlsafe(7)
    data = {
        "name": name,
        "surname": surname,
        "username": username,
        "mobile": "",
        "address": "",
        "postcode": "",
        "country": "",
        "state":  "",
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "email": email,
        "role": role,
        "active": True,
        "namespace": f"mcipolla/{username}",
        "package": package,
        "shared_package": [],
        "chat": [],
        "openapi": openapi,
        "teams": []
    }
    package = requests.post(f"https://walkiria.cloud/api/v1/web/mcipolla/base/package/add", json={"name": username}, headers={'Authorization': 'Bearer ' + token})
    if package.status_code == 200:
        response = requests.post(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/add", json={"data": data}, headers={'Authorization': 'Bearer ' + token})
        if response.status_code == 200:
            return {"statusCode": 200, "body": {"password": password}}
        requests.delete(f"https://walkiria.cloud/api/v1/web/mcipolla/base/package/delete", json={"name": username})
        return {"statusCode": response.status_code, "body": {"error": "Failed creating the user"}}
    return {"statusCode": package.status_code, "body": package.json()}

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
    user = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'_id': id})),
                        headers={"Authorization": "Bearer " + token})
    if user.status_code == 404:
        return {"statusCode": 404}
    response = requests.delete(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/delete?id=" + id,
                        headers={"Authorization": "Bearer " + token})
    if response.status_code == 400:
        return {"statusCode": response.status_code, "body": response.text}
    if user.status_code == 200:
        obj = user.json()
        requests.delete(f"https://walkiria.cloud/api/v1/web/mcipolla/base/package/delete", json={"name": obj['package']},
                        headers={"Authorization": "Bearer " + token})
        return {"statusCode": 204}
    return {"statusCode": response.status_code}

def update(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    data = args.get('data', False)
    id = args.get('id', False)
    if not data or not id:
        return {"statusCode": 400}
    response = requests.put(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/update?id=" + id,
                        json={"data": data},
                        headers={"Authorization": "Bearer " + token})
    if response.status_code == 200:
        return {"statusCode": response.status_code, "body": response.text}
    return {"statusCode": response.status_code}

def find(args):
    id = args.get('id', False)
    if not id:
        return {"statusCode": 400}
    response = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'id': id})))
    if response.status_code != 404:
        return {"statusCode": 200, "body": response.text}
    return {"statusCode": 404}

def find_all(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    response = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_many", headers={'Authorization': 'Bearer ' + token})
    if response.status_code != 404:
        return {"statusCode": 200, "body": response.json()}
    return {"statusCode": 404}

def main(args):
    path = args['__ow_path']
    if path == '/add' and args['__ow_method'] == 'post':
        return create(args)
    elif path == '/delete' and args['__ow_method'] == 'delete':
        return delete(args)
    elif path == '/update' and args['__ow_method'] == 'put':
        return update(args)
    elif path == '/find'and args['__ow_method'] == 'get':
        return find(args)
    elif path == '/find_all'and args['__ow_method'] == 'get':
        return find_all(args)
    elif path == '/pendings'and args['__ow_method'] == 'get':
        return get_pendings(args)
    return {"statusCode": 404}