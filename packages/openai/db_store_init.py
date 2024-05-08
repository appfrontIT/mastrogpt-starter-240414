#--web false
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--timeout 600000

import requests
from requests.auth import HTTPBasicAuth
import os
import json
from itertools import islice
from bs4 import BeautifulSoup
import time

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

def crawl(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching page")
        return ""
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def main(args):
    url = args.get('url', False)
    format = args.get('format', False)
    collection = args.get('collection', False)
    user = args.get('user', False)
    if not url or not format or not collection or not user:
        return {"statusCode": 400, "body": "data incomplete"}
    
    text = crawl(url)
    format_obj = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/utility/extract_keys_from_md?blocking=true', auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), json={
        "md": format
    })
    obj = format_obj.json()
    md = obj['response']['result']['body']
    split = text.splitlines()
    request = f"""
    create an action that will take a 'line' as parameter and store it inside a json.
    The line will be like: {split[0]}, and the json must follow this guidelines: {format}.
    You will find the start and the length of each element inside the guideline.
    The action must return the filled json.
    Use the following name for the action: {collection}_store
    remember to import the necessary libraries
    """
    action = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/openai/create_action?blocking=true',
                        auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                        json={"request": request, "user": user
                            })
    print(action.text)
    action_obj = action.json()
    body = action_obj['response']['result']['body']
    print(body)
    url = body.split("'")[1]
    print(url)
    while True:
        lines = list(islice(split, 500))
        if not lines:
            break
        requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/openai/db_store_exec',
                    auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                    json={"format": md, "collection": collection, "text": lines, "user": user, "url": url}
                    )
        split = split[500:]
        time.sleep(1)
    return {"statusCode": 204}
