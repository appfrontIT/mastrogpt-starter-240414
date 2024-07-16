#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation description "an action that create a chart and return an html page"
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/grapher/bot

from openai import OpenAI
import requests
import config
import json
import bot_functions
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient, errors
from pymongo.collection import Collection
import os

MODEL = "gpt-4o"

def ask(
    messages,
    model: str = MODEL,
) -> str:
    response = config.AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
        temperature=0.1,
        top_p=0.1
    )
    if response.choices[0].finish_reason == "tool_calls":
        return bot_functions.tools_func(messages, response)
    return response.choices[0].message.content

def main(args):
    global AI

    config.AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    config.session_user = args.get('user', False)
    if not config.session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    input = args.get("input", False)
    if not input:
        return {"statusCode": 400, "body": "error: no input provided"}
    config.CLIENT = MongoClient(args.get('CONNECTION_STRING'))
    messages = [{'role': 'system', 'content': config.ROLE}]
    messages.extend(input)
    res = { "output": ask(messages=messages, model=MODEL)}
    if config.showEditor:
        res['showEditor'] = True
    requests.post(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': res})
    return {"statusCode": 200, "body": res }