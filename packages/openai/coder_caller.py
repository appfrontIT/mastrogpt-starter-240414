#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "This action is used to asynchronously call coder"

import requests
from requests.auth import HTTPBasicAuth
import os

def main(args):
    OW_KEY = os.getenv('__OW_API_KEY')
    split = OW_KEY.split(':')
    resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/openai/coder", auth=HTTPBasicAuth(split[0], split[1]), json={"input": args.get('input', '')})
    return {"statusCode": 200, "body": resp.text}