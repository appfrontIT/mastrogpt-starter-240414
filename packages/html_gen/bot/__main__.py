#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which generate an action returning an HTML page"
#--annotation url https://walkiria.cloud/api/v1/web/gporchia/html_gen/create
#--timeout 300000

from openai import OpenAI
import bot_functions
import requests
import config
from requests.auth import HTTPBasicAuth

AI = None
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


TUNED_MODEL = None

def main(args):
    print(args)
    config.AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    
    input = args.get("input", "")
    # user = args.get("user", None)
    if input == "":
        return {"statusCode": 204, }  
    else:
        messages = [{'role': 'system', 'content': config.ROLE}]
        messages.extend(input)
        res = { "output": ask(messages=messages, model=MODEL)}
    editor = {"function": res[ 'output'], "description": '', "name": args.get('name', ''), "namespace": '', "package": '', "language": 'html'}
    requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': args.get('id'), 'message': {'editor': editor, 'output': "Sto creando la pagina seguendo le tue indicazioni per favore attendi"}})
    return {"statusCode": 200, "body": res }

