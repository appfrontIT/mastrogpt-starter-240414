#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action to perform tests on different endpoints"
#--timeout 300000

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
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
        messages.append(response.choices[0].message)
        tool_calls = response.choices[0].message.tool_calls
        for tool_call in tool_calls:
            print(tool_call.function.name)
            function_name = "general_test"
            function_to_call = bot_functions.general_test
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
                )
            messages.append({
                "tool_call_id":tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })
        messages.append({'role': 'user', 'content': 'based on the tests, tell the user how to improve the endpoint to ensure everything is fine'})
        response = config.AI.chat.completions.create(
            model=model,
            messages=messages,
            )
    return response.choices[0].message.content

def main(args):
    config.html = ""
    config.AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    token = args.get('token', False)
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?JWT={token}", headers={'Authorization': f"Bearer {token}"})
    if response.status_code != 200:
        return {"statusCode": 404}
    config.session_user = response.json()

    input = args.get("input", "")
    if input == "":
        res = {
            "output": f"Bentornato {config.session_user['username']}! Cosa vorresti testare?",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
            "html": config.HTML_INFO
        }
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'message': res, 'reset_history': True, 'history': {"role": "system", "content": config.ROLE}})
        return { "statusCode": 204, }  
    else:
        print(input)
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'history': {"role": "user", "content": input }})
        output = ask(query=input, model=MODEL)
        res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return {"statusCode": 200, 'body': res['output']} 
