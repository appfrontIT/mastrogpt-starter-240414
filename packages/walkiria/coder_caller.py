#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action is used to asynchronously call coder"
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
    token = token.split(' ')[1]
    decoded = jwt.decode(token, key=args.get('JWT_SECRET'), algorithms='HS256')
    print(decoded['id'])
    response = requests.post(f'https://nuvolaris.dev/api/v1/web/gporchia/default/user/find?id={decoded['id']}')
    if response.status_code == 404:
        return {"statusCode": 404}
    resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/coder", auth=HTTPBasicAuth(split[0], split[1]), json={"input": args.get('input', ''), 'id': decoded['id']})
    return {"statusCode": 200, "body": resp.text}