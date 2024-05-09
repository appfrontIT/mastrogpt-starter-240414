#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--timeout 600000

import requests
from requests.auth import HTTPBasicAuth
import os
import json
from openai import OpenAI
from bs4 import BeautifulSoup

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
USER = None
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
    user = args.get('user', False)
    url = args.get('url', False)
    print(url)

    if not format or not collection or not text or not user or not url:
        return {"statusCode": 400}

    arr = []
    for line in text:
        response = requests.post(url, json={'line': line})
        if response.status_code == 200:
            arr.append(response.json())
    print(arr)
    insertion = requests.post(
        "https://nuvolaris.dev/api/v1/web/gporchia/db/mongo",
        json={
            "insert_many": True, "db": "mastrogpt", "collection": collection, "data": arr
            })
    print(insertion.text)
    return {"statusCode": 204}
