#--web true
#--kind python:default
#--annotation provide-api-key true

import os
import requests
from requests.auth import HTTPBasicAuth

def main(args):
    print(args)
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    resp = requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{args.get('name')}", auth=HTTPBasicAuth(split[0], split[1]))
    return {"body": resp.text}