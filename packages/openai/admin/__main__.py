#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which interact with a custom bot to invoke administration tasks"

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
import json
import requests
from requests.auth import HTTPBasicAuth

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    query: str,
    model: str = MODEL,
) -> str:
    history = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/get_history", json={'cookie': config.session_user['cookie']})
    messages = json.loads(history.text)
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
        max_tokens=(4096 - 500)
    )
    # We start checking if the tools activated. If not we answer generic question about Nuvolaris
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(AI, tool_calls, messages, response)
    return response.choices[0].message.content

def main(args):
    global AI
    config.html = "<iframe src='https://appfront.cloud' width='100%' height='800'></iframe>"

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    cookie = args['__ow_headers'].get('cookie', False)
    if not cookie:
        return {"statusCode": 302, "headers": {"location": "https://gporchia.nuvolaris.dev"}}
    response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/user/find_by_cookie', json={"cookie": cookie})
    if response.status_code == 404:
        return {"statusCode": 404}
    config.session_user = response.json()
    if config.session_user['role'] != 'admin':
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": {"output": "Devi essere un Admin per poter accedere a questa sessione"}})
        return{"statusCode": 403}
    input = args.get("input", "")
    if input == "":
        res = {
            "output": f"Bentornato {config.session_user['name']}! Come posso aiutarti?",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': cookie, 'message': res, 'reset_history': True, 'history': {"role": "system", "content": config.ROLE}})
        return { "statusCode": 204, }
    else:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': cookie, 'history': {"role": "user", "content": input}})
        output = ask(query=input, model=MODEL)
        res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': cookie, 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return {"statusCode": 204}
