#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action is used invoke bots asynchronously"
#--param JWT_SECRET $JWT_SECRET
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/base/invoke

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
    token = token.split(' ')[1]
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?JWT={token}", headers={'Authorization': f"Bearer {token}"})
    if response.status_code != 200:
        return {"statusCode": 404}
    user = response.json()
    input = args.get('input', '')
    if path == '/walkiria':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": input, 'token': token, 'user': user})
    elif path == '/lookinglass':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/lookinglass/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": input, 'token': token, 'user': user})
    elif path == '/admin':
        secret = args.get('JWT_SECRET')
        decoded = jwt.decode(token, key=secret, algorithms='HS256')
        if decoded['role'] != 'admin':
            return{"statusCode": 403}
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/admin/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": input, 'token': token, 'user': user})
    elif path == '/test':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": input, 'token': token, 'user': user})
    elif path == '/html':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/html_gen/bot",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": input, 'token': token, 'user': user, 'name': args.get('name', '')})
    elif path == '/chat_lookinglass':
        resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/lookinglass/bot?blocking=true",
                            auth=HTTPBasicAuth(split[0], split[1]),
                            json={"input": [{"role": "user", "content": input}], 'token': token, 'user': user})
        if resp.ok:
            obj = resp.json()
            body = obj['response']['result']['body']
            return {'statusCode': resp.status_code, 'body': {'answer': body['output'], 'url': body['frame']}}
        return {'satusCode': resp.status_code}
    return {"statusCode": resp.status_code, "body": resp.json()}