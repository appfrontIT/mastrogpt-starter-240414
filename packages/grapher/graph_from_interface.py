#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation description "an action that create a chart and return an html page"
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/web/gporchia/grapher/graph_from_interface

from openai import OpenAI
import requests
import pandas as pd
import json
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient, errors
from pymongo.collection import Collection
import os

html = ""
editor = ""
session_user = None

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
QUERY: str = ""

AI = None
MODEL = "gpt-4o"

def main(args):
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    id = args.get('id', None)
    if not id:
        return {"statusCode": 404, "body": "no ID provided"}
    input = args.get("input", False)
    if not input:
        return {"statusCode": 400, "body": "error: no input provided"}
    data = args.get('data', None)
    if data == None:
        return {"StatusCode": 400, "body": "data is missing"}
    messages = [
        {"role": "system", "content": """You're a master of creating charts using chart.js API. Follow the user request and create an amazing graph! You have all the time you need, don't rush. YOU MUST USER CHARTJS TO MAKE THE GRAPH.
        To use chart.js you must import it in the following way:
            <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js/dist/chart.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>.
        Answer only and directly with the full html (starting from <!DOCTYPE html>).
        NEVER include the codeblock (```html).
        Also, remember to display the error in case something is going wrong!"""},
    ]
    messages.extend(input)
    messages.extend([{'role': 'user', 'content': "Here's the data you must use in your graph:\n"}])
    url = data.get('url', None)
    if url != None:
        response = requests.post('https://walkiria.cloud/api/v1/web/gporchia/utility/single_page_scrape',
                            json={'url': data.get('url')})
        if response.ok:
            messages.extend([{'role': 'user', 'content': f"data from url:\n{response.text}"}])
        else:
            return {"statusCode": 500, "body": "an error occured while fetching the url"}
    text = data.get('text', None)
    if text:
        messages.extend([{'role': 'user', 'content': f"data from text:\n{text}"}])
    collection = data.get('collection', None)
    if collection != None:
        connection_string = args.get('CONNECTION_STRING', False)
        client = MongoClient(connection_string)
        dbname = client['mastrogpt']
        collection_list = dbname.list_collection_names()
        if collection in collection_list:
            db_coll = dbname[collection]
        else:
            return {"statusCode": 400, "body": "collection provided does not exists"}
        data = db_coll.find({}, {'_id': 0}).limit(10)
        messages.extend([{'role': 'user', 'content': f"""You must call this endpoint to fetch data from database, making the aggregate and call this API: ('https://walkiria.cloud/api/v1/web/gporchia/db/mongo/mastrogpt/{collection}/aggregate, json={{'pipeline': [...]}}).
                        This endpoint require authorization, here's a full example on how to get the token:
                            - let cookie = document.cookie; if (!cookie) return window.location.assign('/login');
                            - response = await fetch('https://walkiria.cloud/api/v1/web/gporchia/base/auth/token?cookie=' + cookie, {{method: 'GET'}});
                            - if (response.ok) {{ const obj = await response.json(); const token = obj['token']}}
                        When calling the db, include the token as a Bearer: {{"Authorization": "Bearer " + token}}
                        Here's a list of the firsts 10 records of the collection:\n{list(data)}\n
                        You must than filter the data and use it in the chart"""}])
    response = AI.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    editor = {"function": response.choices[0].message.content, "description": '', "name": args.get('name', ''), "namespace": '', "package": '', "language": 'html'}
    requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': id, 'message': {'output': response.choices[0].message.content, 'editor': editor}})
    return {"statusCode": 200, "body": { "output": response.choices[0].message.content } }