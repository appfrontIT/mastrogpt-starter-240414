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
import json
import requests
from requests.auth import HTTPBasicAuth
import utils

AI = None
MODEL = "gpt-3.5-turbo"

messages=[{"role": "system", "content": config.EMB}]

def create_action(
        name: str,
        function
        ):
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    body = {
        "namespace": "gporchia",
        "name": name,
        "exec":{"kind":"python:default", "code":function},
        "annotations":[{"key":"web-export", "value":True}, {"key":"raw-http","value":False}, {"key": "final", "value": True}]
        }
    resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
    if resp.status_code != 200:
        return False
    return f"\nhttps://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}"

def ask(
    query: str,
    model: str = MODEL,
    token_budget: int = 8192 - 500,
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
    content = response.choices[0].message.content
    content = content.replace('```', '')
    content = content.replace('python', '')
    content = content.replace('Python', '')
    action_list = utils.get_actions()
    find_name = [
        {"role": "system", "content": f"find an unique name for the passed program. Answer with only 1 word. You can't any use the following words:\n{action_list}"},
        {"role": "user", "content": content}
    ]
    name = AI.chat.completions.create(
        model=model,
        messages=find_name,
    ).choices[0].message.content
    action_url = create_action(name, content)
    if action_url:
        # action_info = utils.action_info(name)
        config.html = f"""
        <head>
        <link rel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/styles/default.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/highlight.min.js"></script>
            <script>hljs.initHighlightingOnLoad();</script>
        </head>
        <body>
            <pre><code class="python"><xmp>{content}</xmp></code></pre>
        </body>
        """
        messages = [
            {"role": "system", "content": "Explain the passed code"},
            {"role": "system", "content": response.choices[0].message.content}
        ]
        response = AI.chat.completions.create(
            model=model,
            messages=messages,
        )
        return f"{response.choices[0].message.content}\n\n**Action URL**:\nhttps://nuvolaris.dev/api/v1/web/gporchia/default/{name}"
    return "Error, something went wrong in creating your action"

TUNED_MODEL = None

def main(args):
    global AI
    global TUNED_MODEL
    config.html = "<iframe src='https://appfront.cloud' width='100%' height='800'></iframe>"
    config.code = ""

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

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
