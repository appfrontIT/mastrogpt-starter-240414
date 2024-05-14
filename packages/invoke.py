#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action is used invoke bots asynchronously"
#--param JWT_SECRET $JWT_SECRET

import requests
from requests.auth import HTTPBasicAuth
import os
import jwt

def main(args):
    OW_KEY = os.getenv('__OW_API_KEY')
    split = OW_KEY.split(':')

    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    path = args['__ow_path']
    if path == '/walkiria':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": args.get('input', ''), 'token': token,})
    elif path == '/lookinglass':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/lookinglass/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": args.get('input', ''), 'token': token,})
    elif path == '/admin':
        secret = args.get('JWT_SECRET')
        decoded = jwt.decode(token.split(' ')[1], key=secret, algorithms='HS256')
        if decoded['role'] != 'admin':
            return{"statusCode": 403}
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/admin/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": args.get('input', ''), 'token': token,})
    return {"statusCode": resp.status_code, "body": resp.json()}