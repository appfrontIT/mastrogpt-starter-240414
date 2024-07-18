#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/base/package

import os
import requests
from requests.auth import HTTPBasicAuth
import urllib
import json

OW_KEY = os.getenv('__OW_API_KEY')
SPLIT = OW_KEY.split(':')

def find_all(args):
    response = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]))
    if response.status_code != 404:
        token = args['__ow_headers'].get('authorization')
        user = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'JWT': token.split(' ')[1]})),
                        headers={"Authorization": token})
        if user.ok:
            obj = user.json()
            if obj['role'] == 'admin' or obj['role'] == 'root':
                return {"statusCode": 200, "body": response.json()}
            packages: list = obj['package'] + obj['shared_package']
            packages_arr = []
            for pack in response.json():
                for pack2 in packages:
                    if pack['name'] == pack2:
                        packages_arr.append(pack)
            return {"statusCode": 200, "body": packages_arr}
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
    resp = requests.put(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{name}",
                    auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]),
                    headers={"Content-type": "application/json"}, json=body)
    if resp.ok:
        token = args['__ow_headers'].get('authorization')
        user = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'JWT': token.split(' ')[1]})),
                        headers={"Authorization": token})
        if user.ok:
            obj = user.json()
            packages: list = obj['package']
            packages.append(name)
            update = requests.put(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/update?id={str(obj['_id'])}",
                            json={'data': {'package': packages}},
                            headers={"Authorization": args['__ow_headers'].get('authorization')})
            return {'statusCode': update.status_code, 'body': update.json()}
    return {"statusCode": resp.status_code, 'body': resp.json()}

def share(args):
    id = args.get('id', False)
    package = args.get('package', False)
    if not id or not package:
        return {'statusCode': 400}
    resp = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{package}", auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]))
    if resp.status_code != 200:
        return {'statusCode': 404, 'body': f'package {package} not found'}
    user = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'_id': id})),
                        headers={"Authorization": args['__ow_headers'].get('authorization')})
    if user.status_code == 200:
        obj = user.json()
        shared_package: list = obj['shared_package']
        if package not in shared_package:
            shared_package.append(package)
        update = requests.put(f'https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/update?id={id}',
                            json={'data': {'shared_package': shared_package}},
                            headers={"Authorization": args['__ow_headers'].get('authorization')})
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