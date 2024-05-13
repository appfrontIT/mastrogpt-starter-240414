#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "use this endpoint to perform operations with action. You must specify the operation correspondig path: '/add', '/update', '/delete', '/find'"
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param JWT_SECRET $JWT_SECRET

import jwt
import requests
from requests.auth import HTTPBasicAuth
import os

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
USER: None

def add(args):
    name = args.get('name', False)
    function = args.get('function', False)
    description = args.get('description', False)
    if not function and not name and not description:
        return {'statusCode': 400}
    url = f"https://nuvolaris.dev/api/v1/web/gporchia/{USER['package']}/{name}"
    body = {
        "namespace": "gporchia/" + USER['package'],
        "name": name,
        "exec":{"kind":"python:default", "code":function},
        "annotations":[
            {"key":"web-export", "value":True},
            {"key":"raw-http","value":False},
            {"key": "final", "value": True},
            {"key": "description", "value": description},
            {"key": "url", "value": url}
            ]
        }
    if USER['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{USER['package']}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    return {'statusCode': resp.status_code, 'body': resp.json()}

def delete(args):


def update(args):


def find(args):


def main(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    decoded = jwt.decode(token, key=secret, algorithms='HS256')
    global USER
    response = requests.get(f'https://nuvolaris.dev/api/v1/web/gporchia/default/user/find?id={decoded['id']}')
    if response.status_code == 200:
        USER = response.json()
    else:
        return {'statusCode': 404, 'body': 'user not found'}
    path = args.get('__ow_path', False)
    if path == '/add' and args['__ow_method'] == 'post':
        return add(args)
    if path == '/delete' and args['__ow_method'] == 'delete':
        return delete(args)
    if path == '/update' and args['__ow_method'] == 'put':
        return update(args)
    if path == '/find' and args['__ow_method'] == 'get':
        return find(args)
    return {"statusCode": 404}