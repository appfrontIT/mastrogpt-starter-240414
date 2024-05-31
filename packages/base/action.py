#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "use this endpoint to perform operations with action. You must specify the operation correspondig path: '/add', '/update', '/delete', '/find'"
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param JWT_SECRET $JWT_SECRET
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/base/action

import jwt
import requests
from requests.auth import HTTPBasicAuth
import os

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
JWT: None

def add(args, token):
    name = args.get('name', False)
    package = args.get('package', False)
    function = args.get('function', False)
    description = args.get('description', False)
    language = args.get('language', False)
    if not function or not name or not description or not language or not package:
        return {'statusCode': 400}
    url = f"https://nuvolaris.dev/api/v1/web/gporchia/{package}/{name}"
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
            {"key": "url", "value": url}
            ]
        }
    if package == 'default':
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    requests.post('https://nuvolaris.dev/api/v1/web/gporchia/walkiria/openAPI/add',
                headers={'Authorization': 'Bearer ' + token},
                json={'action': f"""url: https://nuvolaris.dev/api/v1/web/gporchia/{package}/{name}\ndescription: {description}\nfunction: {function}""", 'token': token})
    return {'statusCode': resp.status_code, 'body': resp.json()}

def delete(args):
    name = args.get('name', False)
    package = args.get('package', False)
    if not name or not package:
        return {'statusCode': 400}
    if package not in JWT['package']:
        return {'statusCode': 404}
    response = requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}",
                    auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    if response.status_code == 204:
        return {'statusCode': response.status_code}
    return {'statusCode': response.status_code, 'body': response.json()}

def update(args):
    return(add(args=args))

def find(args):
    name = args.get('name', False)
    package = args.get('package', False)
    if not name or not package:
        return {'statusCode': 400}
    if package not in JWT['package'] and JWT['role'] != 'admin':
        return {'statusCode': 404}
    action = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return {'statusCode': action.status_code, 'body': action.json()}

def find_all():
    if JWT['role'] == 'admin':
        response = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
        if response.status_code == 200:
            packages = []
            for el in response.json():
                packages.append(el['name'])
    else:
        packages = JWT['package']
    ret = []
    for package in packages:
        response = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{package}", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
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
    if path == '/add' and (args['__ow_method'] == 'post' or args['__ow_method'] == 'put'):
        return add(args, token)
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