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

MODEL = "gpt-4o"
AI = None

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
    config.html = ""
    config.AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    config.session_user = args.get('user', False)
    if not config.session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    input = args.get("input", "")
    if input == "":
        return { "statusCode": 204, }
    else:
        config.query = input
        messages = [{'role': 'system', 'content': config.ROLE}]
        messages.extend(input)
        res = { "output": ask(messages=messages, model=MODEL)}
    if config.frame != "":
        res['frame'] = config.frame
    if config.base64_pdf != "":
        res['pdf'] = config.base64_pdf
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': res, 'history': {"role": "assistant", "content": res['output']}})
    return { "statusCode": 200, 'body': res}
