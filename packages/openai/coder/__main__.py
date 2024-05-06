#--web false
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which interact with a custom bot that generate actions"
#--timeout 600000

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
    # config.expand = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/prefetch/coder', json={"input": query, 'package': config.package}).text
    history = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/get_history", json={'cookie': config.session_user['cookie']})
    messages = json.loads(history.text)
    response = config.AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
    )
    # We start checking if the tools activated. If not we answer generic question about Nuvolaris
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        print(response.choices[0])
        return bot_functions.tools_func(tool_calls, messages, response)
    print("no tools")
    return response.choices[0].message.content

def main(args):
    config.html = ""
    config.AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    cookie = args.get('cookie', False)
    response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/user/find_by_cookie', json={"cookie": cookie})
    if response.status_code == 404:
        return {"statusCode": 404}
    config.session_user = response.json()

    input = args.get("input", "")
    if input == "":
        res = {
            "output": f"Bentornato {config.session_user['name']}! Come posso aiutarti?",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
            "html": config.HTML_INFO
        }
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], 'message': res, 'reset_history': True, 'history': {"role": "system", "content": config.EMB}})
        return { "statusCode": 204, }  
    else:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], 'history': {"role": "user", "content": input }})
        output = ask(query=input, model=MODEL)
        res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return {"statusCode": 204}
