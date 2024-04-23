#--web true
#--kind python:default
#--annotation provide-api-key true
#--annotation description "an action which add a package to nuvolaris. Required parameters: {'name': package name}"

import os
import requests
from requests.auth import HTTPBasicAuth

def main(args):
   ow_key = os.getenv('__OW_API_KEY')
   split = ow_key.split(':')
   body = {
      "namespace": "gporchia",
      "name": args.get('name'),
      "publish": False
      }
   resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{args.get('name')}", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
   return {"body": resp.text}