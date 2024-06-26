#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}"
#--param JWT_SECRET $JWT_SECRET
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/base/user

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
    if role != 'user' and role != 'admin':
        return {'statusCode': 400, 'body': 'role invalid. Must be one of: user, admin'}
    openapi = f"""{{
        "openapi": "3.1.0",
        "info": {{
            "title": "{username} - OpenAPI 3.1",
    "termsOfService": "http://swagger.io/terms/",
    "version": "1.0.11"
    }},
    "servers": [{{"url": "https://nuvolaris.dev/api/v1/web"}}],
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
    data = {
        "username": username,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": role,
        "namespace": f"gporchia/{username}",
        "package": package,
        "shared_package": [],
        "chat": [],
        "openapi": openapi,
        "teams": []
    }
    package = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/base/package/add", json={"name": username}, headers={'Authorization': 'Bearer ' + token})
    if package.status_code == 200:
        response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/add", json={"data": data}, headers={'Authorization': 'Bearer ' + token})
        if response.status_code == 200:
            return {"statusCode": 200, "body": response.json()}
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/base/package/delete", json={"name": username})
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
        requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/base/package/delete", json={"name": obj['package']})
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

def find_all(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_many", headers={'Authorization': 'Bearer ' + token})
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
    return {"statusCode": 404}