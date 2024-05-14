#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which interact with a custom bot that generate actions"
#--timeout 300000

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
import utils
import json
import requests
import os
from requests.auth import HTTPBasicAuth

MODEL = "gpt-3.5-turbo"

def ask(
    query: str,
    model: str = MODEL,
) -> str:
    history = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/get_history", json={'id': config.session_user['_id']})
    messages = json.loads(history.text)
    response = config.AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
    )
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(tool_calls, messages, response)
    print("no tools")
    return response.choices[0].message.content

def main(args):
    config.html = ""
    config.AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    token = args.get('token', False)
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?JWT={token.split(' ')[1]}", headers={'Authorization': token})
    if response.status_code != 200:
        return {"statusCode": 404}
    config.session_user = response.json()

    input = args.get("input", "")
    if input == "":
        res = {
            "output": f"Bentornato {config.session_user['username']}! Come posso aiutarti?",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
            "html": config.HTML_INFO
        }
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'message': res, 'reset_history': True, 'history': {"role": "system", "content": config.ROLE}})
        return { "statusCode": 204, }  
    else:
        config.QUERY = input
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'history': {"role": "user", "content": input }})
        output = ask(query=input, model=MODEL)
        res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return {"statusCode": 200, 'body': res['output']} 
