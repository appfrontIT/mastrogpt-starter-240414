#--web true
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "thi action will ensure better output from the agent providing more informations to the request"
#--timeout 300000

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import json
import requests
import config
import os

AI = None

def ask(query: str, model: str = config.MODEL) -> str:
    messages = [
        {"role": "system", "content": config.EMB},
        {"role": "user", "content": f"Generate a request improving the following query adding informations on how to build the action.\nquery:\n{query}"},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content

def main(args):
    global AI
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    input = args.get("input", "")
    print(input)
    output = ask(query=input, model=config.MODEL)
    return {"body": {"output": output}}