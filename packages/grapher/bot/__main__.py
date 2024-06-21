#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation description "an action that create a chart and return an html page"
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/grapher/bot

from openai import OpenAI
import requests
import config
import json
from requests.auth import HTTPBasicAuth

AI = None
MODEL = "gpt-4o"

def main(args):
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    config.session_user = args.get('user', False)
    if not config.session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    input = args.get("input", False)
    if not input:
        return {"statusCode": 400, "body": "error: no input provided"}
    messages = [{'role': 'system', 'content': config.ROLE}]
    messages.extend(input)
    response = AI.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': {'output': response.choices[0].message.content,}})
    return {"statusCode": 200, "body": { "output": response.choices[0].message.content } }