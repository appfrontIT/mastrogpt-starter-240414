#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which interact with a custom bot to invoke administration tasks"
#--annotation url https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/admin/bot

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
    history = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/get_history", json={'id': config.session_user['_id']})
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
    config.html = ""
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    config.session_user = args.get('user', False)
    if not config.session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    
    input = args.get("input", "")
    if input == "":
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'reset_history': True, 'history': {"role": "system", "content": config.ROLE}})
        return { "statusCode": 204, }
    else:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'history': {"role": "user", "content": input}})
        output = ask(query=input, model=MODEL)
        res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return {"statusCode": 204}
