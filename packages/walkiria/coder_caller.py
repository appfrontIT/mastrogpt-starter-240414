#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action is used to asynchronously call coder"

import requests
from requests.auth import HTTPBasicAuth
import os

def main(args):
    OW_KEY = os.getenv('__OW_API_KEY')
    print(OW_KEY)
    split = OW_KEY.split(':')

    cookie = args['__ow_headers'].get('cookie', False)
    cookie_split = cookie.split('=')

    response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/user/find_by_cookie', json={"cookie": cookie_split[1]})
    if response.status_code == 404:
        return {"statusCode": 404, "body": {"cookie": cookie_split[0]}}
    
    resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/coder", auth=HTTPBasicAuth(split[0], split[1]), json={"input": args.get('input', ''), 'cookie': cookie_split[1]})
    return {"statusCode": 200, "body": resp.text}