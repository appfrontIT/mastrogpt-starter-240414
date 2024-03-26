#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import os
import re
import requests
from requests.auth import HTTPBasicAuth

def create_function(function_name, function_arguments, function_code):
    function_string = f"def {function_name}({function_arguments}): {function_code}"
    exec(function_string)
    return_value = eval(function_name)
    return return_value

AI = None
MODEL = "gpt-3.5-turbo"

messages=[{"role": "system", "content": config.EMB}]

def ask(
    query: str,
    model: str = MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    messages = [
        {"role": "system", "content": config.EMB},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    response_message = response.choices[0].message.content
    return response_message

TUNED_MODEL = None

def main(args):
    global AI
    global TUNED_MODEL
    global api_key
    config.html = "<iframe src='https://appfront.cloud' width='100%' height='800'></iframe>"

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    # print(ow_key)
    dele = requests.delete("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/test", auth=HTTPBasicAuth(split[0], split[1]))
    # print(dele.text)
    body = {
        "namespace": "gporchia",
        "name": "hello",
        "exec":{"kind":"python:default", "code":"def main(params):\n\treturn {'body':'Hello ' + str(params.get('name'))}"},
        "annotations":[{"key":"web-export", "value":True}, {"key": "final", "value": False}]
        }
    resp = requests.put("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/test", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
    print(resp.text)

    test = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/test", auth=HTTPBasicAuth(split[0], split[1]), json={"name": "Matteo"})
    print(test.text)

    TUNED_MODEL = MODEL

    input = args.get("input", "")
    if input == "":
        res = {
            "output": "Benvenuti in Walkiria, la piattaforma AI di Appfront.",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    elif input[len(input) -1] == ' ':
        return {"body": {"output": ""}}
    else:
        output = ask(query=input, print_message=False, model=TUNED_MODEL)
        res = {
            "output": output
        }
    if config.html != "":
        res['html'] = config.html
    return {"body": res }
