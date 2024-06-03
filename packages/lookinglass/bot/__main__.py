#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description 'an action which let you interact with a custom assistant helping you in Lookinglass operations'
#--annotation url https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/lookinglass/bot

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import requests
import re
import os
import veichle
import config
import ast
import pandas as pd
import tiktoken
from scipy import spatial
import bot_functions
import json
import man
from requests.auth import HTTPBasicAuth

MODEL = "gpt-3.5-turbo"
AI = None

available_functions = {
    "quotation_by_birth": veichle.quotation_by_birth,
    "quotation_by_cf": veichle.quotation_by_cf,
    "find_man_page": man.find_man_page
}

messages = [{'role': 'system', 'content': config.ROLE}]

def ask(
    query: str,
    model: str = MODEL,
) -> str:
    config.query = query
    messages.extend(query)
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.quotation_functions,
        tool_choice="auto"
    )
    if response.choices[0].finish_reason == "tool_calls":
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], "message": {"output": "Certamente, procedo subito ad elaborare la tua richiesta"}})
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)
        for tool_call in tool_calls:
            print(tool_call.function.name)
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
                )
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })
        response = AI.chat.completions.create(
            model=model,
            messages=messages,
        )
    else:
        print('no tools')
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
        return { "statusCode": 204, }
    else:
        output = ask(query=input, model=MODEL)
        res = { "output": output }
    if config.frame != "":
        res['frame'] = config.frame
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return { "statusCode": 204, }
