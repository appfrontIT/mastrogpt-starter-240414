from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils
import requests
from requests.auth import HTTPBasicAuth
import os

html = ""
nuvolaris = []

nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/actions.html"))
nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/webactions.html"))
nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/parameters.html"))
nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/annotations.html"))

MODEL = "gpt-3.5-turbo"
EMB = f"""
From now on you are a programming language. You only know Python.
Your job is to create functions to be deployed to Nuvolaris.
- the function you generate MUST have at least the "main", and needs to return a dictionary or aray with key "body". Any other return type is forbidden
- the "main" always accept "(args)"
- NEVER use async
- import any library you use
- if you need to accept parameters you will get those such as: args.get("url") to get "url", args.get("name") to get "name" and so on
- you can use only the follow libraries:
aiohttp v1.3.3
appdirs v1.4.3
asn1crypto v0.21.1
async-timeout v1.2.0
attrs v16.3.0
beautifulsoup4 v4.5.1
cffi v1.9.1
chardet v2.3.0
click v6.7
cryptography v1.8.1
cssselect v1.0.1
gevent v1.2.1
greenlet v0.4.12
httplib2 v0.9.2
idna v2.5
itsdangerous v0.24
Jinja2 v2.9.5
kafka-python v1.3.1
lxml v3.6.4
MarkupSafe v1.0
multidict v2.1.4
packaging v16.8
parsel v1.1.0
pyasn1 v0.2.3
pyasn1-modules v0.0.8
pycparser v2.17
PyDispatcher v2.0.5
pyOpenSSL v16.2.0
pyparsing v2.2.0
python-dateutil v2.5.3
queuelib v1.4.2
requests v2.11.1
Scrapy v1.1.2
service-identity v16.0.0
simplejson v3.8.2
six v1.10.0
Twisted v16.4.0
w3lib v1.17.0
Werkzeug v0.12
yarl v0.9.8
zope.interface v4.3.3
"""

EXTRACT_DATA ="""
you analyze the text and extract the name of the action and the function
if both are no present, don't call the function and answer with the element missing
"""

def exec_find_func(
        name: str,
        language: str,
        function
        ):
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    print("name " + name)
    print("langue " + language)
    print(function[:20])
    kind = ""
    if language.lower() == 'python':
        kind = "python:default"
    if language.lower() == 'nodejs':
        kind = "nodejs:20"
    body = {
        "namespace": "gporchia",
        "name": name,
        "exec":{"kind":kind, "code":function},
        "annotations":[{"key":"web-export", "value":True}, {"key":"raw-http","value":False}, {"key": "final", "value": True}]
        }
    resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
    if resp.status_code != 200:
        return "Couldn't create the action"
    config.html += f"\nhttps://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}"
    return "action deployed"


def find_func(
        AI: OpenAI,
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
) -> str:
    available_functions = {
        "exec_find_func": exec_find_func,
        }
    messages.append(response.choices[0].message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
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
    response = AI.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

func_finder = [
    {
        "type": "function",
        "function": {
            "name": "exec_find_func",
            "description": "find the function, the programming language inside the text, and name of the action",
            "parameters": {
                "type": "object",
                "properties": {
                    "name" : {"type": "string", "description": "single word that identify the action"},
                    "language" : {"type": "string", "description": "programming language of the function"},
                    "body": { "type": "string", "description": "the full message"},
                    },
                    "required": ["name", "language", "function"],
                },
            }
        },
]

find_action = [
    {
        "type": "function",
        "function": {
            "name": "get_action",
            "description": "Find 'action' name inside text ",
            "parameters": {
                "type": "object",
                "properties": {
                    "name" : {"type": "string", "description": "single word that identify the action"},
                    },
                    "required": ["name"],
                },
            }
        },
]