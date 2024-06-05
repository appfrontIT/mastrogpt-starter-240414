#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which interact with a custom bot that generate actions"
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/bot

from openai import OpenAI
import config
import bot_functions
import json
import requests
from requests.auth import HTTPBasicAuth

MODEL = "gpt-4o"

def ask(
    messages: str,
    model: str = MODEL,
) -> str:
    response = config.AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
    )
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(tool_calls, messages, response)
    return response.choices[0].message.content

def main(args):
    config.html = ""
    config.AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    config.session_user = args.get('user', False)
    if not config.session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    input = args.get("input", "")
    if input == "":
        return { "statusCode": 204, }  
    else:
        messages = [{'role': 'system', 'content': config.ROLE}]
        messages.extend(input)
        res = { "output": ask(messages=messages, model=MODEL)}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'cookie': config.session_user['cookie'], 'message': res})
    return {"statusCode": 200, 'body': res['output']} 
