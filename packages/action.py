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
JWT: None

def add(args):
    name = args.get('name', False)
    function = args.get('function', False)
    description = args.get('description', False)
    if not function or not name or not description:
        return {'statusCode': 400}
    url = f"https://nuvolaris.dev/api/v1/web/gporchia/{JWT['package']}/{name}"
    body = {
        "namespace": "gporchia/" + JWT['package'],
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
    if JWT['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{JWT['package']}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    return {'statusCode': resp.status_code, 'body': resp.json()}

def delete(args):
    name_array = args.get('actions', False)
    if not name_array:
        return {'statusCode': 400}
    to_obj = []
    for name in name_array:
        item = requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{JWT['package']}/{name}",
                        auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
        to_obj.append(item.json)
    return {'statusCode': 200, 'body': to_obj}

def update(args):
    name = args.get('name', False)
    function = args.get('function', False)
    description = args.get('description', False)
    if not function or not name or not description:
        return {'statusCode': 400}
    if JWT['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={
            "name": name,
            "exec":{"kind":"python:default", "code":function},
            "annotations":[{"key": "description", "value": description},]
        })
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{JWT['package']}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={
            "name": name,
            "exec":{"kind":"python:default", "code":function},
            "annotations":[{"key": "description", "value": description},]
        })
    return {'statusCode': resp.status_code, 'body': resp.json()}

def find(args):
    name = args.get('name', False)
    if not name:
        return {'statusCode': 400}
    action = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{JWT['package']}/{name}",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {'statusCode': action.status_code, 'body': action.json()}

def find_all():
    actions = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {'statusCode': actions.status_code, 'body': actions.json()}

def activation(args):
    id = args.get('id', False)
    if not id:
        return {'statusCode': 400}
    action = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/activations/{id}/result", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {'statusCode': action.status_code, 'body': action.json()}

def main(args):
    global JWT
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(token, key=secret, algorithms='HS256')
    path = args.get('__ow_path', False)
    if path == '/add' and args['__ow_method'] == 'post':
        return add(args)
    elif path == '/delete' and args['__ow_method'] == 'delete':
        return delete(args)
    elif path == '/update' and args['__ow_method'] == 'put':
        return update(args)
    elif path == '/find' and args['__ow_method'] == 'get':
        return find(args)
    elif path == '/find_all' and args['__ow_method'] == 'get':
        return find_all()
    elif path == '/activation' and args['__ow_method'] == 'get':
        return activation(args)
    return {"statusCode": 404}