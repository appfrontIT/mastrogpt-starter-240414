#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "use this endpoint to perform operations with action. You must specify the operation correspondig path: '/add', '/update', '/delete', '/find'"
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param JWT_SECRET $JWT_SECRET
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/base/action

import jwt
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import urllib.parse

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
JWT: None

def add(args, token):
    name = args.get('name', None)
    package = args.get('package', None)
    function = args.get('function', None)
    description = args.get('description', None)
    language = args.get('language', None)
    returns = args.get('returns', None)
    if not function or not name or not description or not language or not package:
        return {'statusCode': 400}
    url = f"https://walkiria.cloud/api/v1/web/mcipolla/{package}/{name}"
    if language == 'python':
        kind = 'python:default'
    elif language == 'javascript':
        kind = 'nodejs:20'
    elif language == 'go':
        kind = 'go:1.22'
    elif language == 'php':
        kind = 'php:7.4'
    body = {
        "namespace": "gporchia/" + package,
        "name": name,
        "exec":{"kind":kind, "code":function},
        "annotations":[
            {"key":"web-export", "value":True},
            {"key":"raw-http","value":False},
            {"key": "final", "value": True},
            {"key": "description", "value": description},
            {"key": "url", "value": url},
            {"key": "return", "value": returns}
            ]
        }
    if package == 'default':
        resp = requests.put(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/{package}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    r = requests.post(f'https://walkiria.cloud/api/v1/web/mcipolla/base/openAPI/add',
                headers={'Authorization': 'Bearer ' + token},
                json={'action': f"""url: https://walkiria.cloud/api/v1/web/mcipolla/{package}/{name}\ndescription: {description}\nfunction: {function}""", 'token': token})
    return {'statusCode': resp.status_code, 'body': resp.json()}

def delete(args):
    name = args.get('name', False)
    package = args.get('package', False)
    if not name or not package:
        return {'statusCode': 400}
    if package not in JWT['package'] and JWT['role'] != 'admin':
        return {'statusCode': 404}
    response = requests.delete(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/{package}/{name}",
                    auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    # if response.ok:
    #     del_from_openapi = requests.delete(
    #         'https://walkiria.cloud/api/v1/web/mcipolla/base/openAPI/delete?action=' + f"/gporchia/{package}/{name}",
    #         headers={'Authorization': args['__ow_headers'].get('authorization')}
    #         )
    #     if not del_from_openapi.ok:
    #         return {'statusCode': 200, 'body': "action successfully deleted, but failed to remove it from openAPI"}
    #     return {'statusCode': response.status_code}
    return {'statusCode': response.status_code, 'body': response.json()}

def update(args):
    return(add(args=args))

def find(args):
    name = args.get('name', False)
    package = args.get('package', False)
    if not name or not package:
        return {'statusCode': 400}
    if package not in JWT['package'] and (JWT['role'] != 'admin' and JWT['role'] != 'root'):
        return {'statusCode': 404}
    action = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/{package}/{name}",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {'statusCode': action.status_code, 'body': action.json()}

def find_all(token):
    if JWT['role'] == 'admin' or JWT['role'] == 'root':
        response = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
        if response.status_code == 200:
            packages = []
            for el in response.json():
                packages.append(el['name'])
    else:
        user = requests.get(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/users/find_one?filter=" + urllib.parse.quote(json.dumps({'JWT': token})),
                        headers={"Authorization": "Bearer " + token})
        if user.ok:
            obj = user.json()
            packages: list = obj['package'] + obj['shared_package']
    ret = []
    for package in packages:
        response = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/{package}", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
        if response.status_code == 200:
            obj = response.json()
            actions = obj['actions']
            for action in actions:
                annotations = action['annotations']
                url = ''
                i = 0
                for an in annotations:
                    if an['key'] == 'url':
                        url = an['value']
                        annotations.pop(i)
                        action['annotation'] = annotations
                        break
                    i += 1
                ret.append({'package': obj['name'], 'name': action['name'], 'annotations': action['annotations'], 'url': url})
    if len(ret) == 0:
        return {'statusCode': 404}
    return {'statusCode': 200, 'body': ret}

def activation(id = None):
    if not id:
        return {'statusCode': 400}
    info = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/activations/{id}", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {'statusCode': 200, 'body': info.json()}

def activations(args):
    name = args.get('name', None)
    if name:
        actions = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/activations",
                            params={"name": name},
                            auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    else:
        actions = requests.get(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/activations", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {"statusCode": actions.status_code, "body": actions.json()}

def main(args):
    global JWT
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(token, key=secret, algorithms='HS256')
    path = args.get('__ow_path', False)
    if path == '/add' and (args['__ow_method'] == 'post' or args['__ow_method'] == 'put'):
        return add(args, token)
    elif path == '/delete' and args['__ow_method'] == 'delete':
        return delete(args)
    elif path == '/update' and args['__ow_method'] == 'put':
        return update(args)
    elif path == '/find' and args['__ow_method'] == 'get':
        return find(args)
    elif path == '/find_all' and args['__ow_method'] == 'get':
        return find_all(token)
    elif path == '/activations' and args['__ow_method'] == 'get':
        return activations(args)
    elif path == '/activation' and args['__ow_method'] == 'get':
        return activation(args.get('id', None))
    return {"statusCode": 404}