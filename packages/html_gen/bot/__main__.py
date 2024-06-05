#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which generate an action returning an HTML page"
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/html_gen/create

from openai import OpenAI
import bot_functions
import requests
import config
from requests.auth import HTTPBasicAuth

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    messages,
    model: str = MODEL,
) -> str:
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content

TUNED_MODEL = None

def main(args):
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    input = args.get("input", "")
    if input == "":
        return {"statusCode": 204, }  
    else:
        messages = [
            {'role': 'system', 'content': config.ROLE},
            {'role': 'user', 'content': input}
            ]
        res = { "output": ask(messages=messages, model=MODEL)}
    return {"statusCode": 200, "body": res }

