#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/base/package

import os
import requests
from requests.auth import HTTPBasicAuth
OW_KEY = os.getenv('__OW_API_KEY')
SPLIT = OW_KEY.split(':')

def find_all(args):
    response = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]))
    if response.status_code != 404:
        return {"statusCode": 200, "body": response.json()}
    return {"statusCode": 404}

def find(args):
    name = args.get('name', False)
    if not name:
        return {"statusCode": 400}
    resp = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{name}", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]))
    return {"statusCode": resp.status_code, "body": resp.text}

def delete(args):
    name = args.get('name', False)
    if not name:
        return {"statusCode": 400}
    resp = requests.delete(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{name}?force=true", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]))
    return {"statusCode": 200, "body": resp.json()}

def add(args):
    name = args.get('name', False)
    if not name:
        return {"statusCode": 400}
    body = {
        "namespace": "mcipolla",
        "name": name,
        "publish": False,
        }
    resp = requests.put(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{name}", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    return {"statusCode": resp.status_code, 'body': resp.json()}

def share(args):
    id = args.get('id', False)
    packages = args.get('packages', False)
    if not id or not packages:
        return {'statusCode': 400}
    for name in packages:
        resp = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{name}", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]))
        if resp.status_code != 200:
            return {'statusCode': 404, 'body': f'package {name} not found'}
    user = requests.get(f'https://walkiria.cloud/api/v1/web/mcipolla/base/user/find?id={id}')
    if user.status_code == 200:
        obj = user.json()
        shared_package: list = obj['shared_package']
        for name in packages:
            if name not in shared_package:
                shared_package.append(name)
        update = requests.put(f'https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/update?id={id}', json={'data': {'shared_packaged': shared_package}})
        return {'statusCode': update.status_code, 'body': update.json()}
    return {'statusCode': user.status_code}

def main(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    path = args.get('__ow_path', False)
    if path == '/add' and args['__ow_method'] == 'post':
        return add(args)
    elif path == '/delete' and args['__ow_method'] == 'delete':
        return delete(args)
    elif path == '/share' and args['__ow_method'] == 'put':
        return share(args)
    # elif path == '/update':
    #     if args['__ow_method'] != 'put':
    #         return {"statusCode": 405}
    #     return update(args)
    elif path == '/find' and args['__ow_method'] == 'get':
        return find(args)
    elif path == '/find_all' and args['__ow_method'] == 'get':
        return find_all(args)
    return {"statusCode": 404}