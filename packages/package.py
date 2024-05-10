#--web true
#--kind python:default
#--annotation provide-api-key true

import os
import requests
from requests.auth import HTTPBasicAuth

def find(args):
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    name = args.get('name', False)
    if not name:
        return {"statusCode": 400}
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{name}", auth=HTTPBasicAuth(split[0], split[1]))
    return {"statusCode": 200, "body": resp.text}

def delete(args):
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    name = args.get('name', False)
    if not name:
        return {"statusCode": 400}
    resp = requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{name}", auth=HTTPBasicAuth(split[0], split[1]))
    return {"statusCode": 200, "body": resp.text}

def create(args):
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    name = args.get('name', False)
    if not name:
        return {"statusCode": 400}
    body = {
        "namespace": "gporchia",
        "name": name,
        "publish": False
        }
    resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{name}", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
    return {"statusCode": resp.status_code}

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
    # elif path == '/update':
    #     if args['__ow_method'] != 'put':
    #         return {"statusCode": 405}
    #     return update(args)
    elif path == '/find':
        if args['__ow_method'] != 'get':
            return {"statusCode": 405}
        return find(args)
    return {"statusCode": 400}