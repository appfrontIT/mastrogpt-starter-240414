#--web false
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--timeout 20000

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

def crawl(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching page")
        return ""
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def main(args):
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    url = args.get('url', False)
    format = args.get('format', False)
    collection = args.get('collection', False)
    if not url or not format or not collection:
        return {"statusCode": 400, "body": "data incomplete"}
    
    text = crawl(url)
    print(format)
    for line in text.splitlines():
        messages = [
            {"role": "system", "content": ROLE},
            {"role": "user", "content": f"generate a JSON based on the following line{line}.\nYou must create the correct keys following this guidelines:\n{format}\nTake your time to understand the forma, It's extremely important!"}
            ]
        response = AI.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            response_format={"type": "json_object"},
        )
        print(response.choices[0].message)
        insertion = requests.post(
            "https://nuvolaris.dev/api/v1/web/gporchia/db/mongo",
            json={
                "add": True, "db": "mastrogpt", "collection": collection, "data": json.dumps(response.choices[0].message.content)
                })
        print(insertion.text)
    return {"statusCode": 204}
