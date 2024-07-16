#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--timeout 600000
#--annotation url https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/db_store_exec

import requests
from requests.auth import HTTPBasicAuth
import os
import json
from openai import OpenAI
from bs4 import BeautifulSoup

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
NAME = ""
ROLE = """You will get a link to some data and some instructions on how to store that data inside the database.
You have to create the correct object to store inside the database.
Read carefully the user instructions before performing any task.
Take your time, don't rush. Correctness of data is crucial.
You must answer in valid JSON format
"""

def main(args):
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    format = args.get('format', False)
    collection = args.get('collection', False)
    text = args.get('text', False)
    url = args.get('url', False)

    if not format or not collection or not text or not url:
        return {"statusCode": 400}

    arr = []
    for line in text:
        response = requests.post(url, json={'line': line})
        if response.status_code == 200:
            arr.append(response.json())
    insertion = requests.post(f"https://walkiria.cloud/api/v1/web/mcipolla/db/mongo/{collection}/add_many", json={"data": arr})
    return {"statusCode": 204}
