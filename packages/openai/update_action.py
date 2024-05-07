#--web false
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--timeout 300000

import requests
from requests.auth import HTTPBasicAuth
import os
import json
from openai import OpenAI

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
USER = None
NAME = ""
ROLE ="""
Your role is to update an action based on the tests suggestions.
Take your time to answer and you must procede step by step.
Function ALWAYS start with "def main(args):".
The return is always: {"body": string}. Example: '{"body": text}', '{"body": response.text}.
It's important to import the modules you will use. Example: import requests, import os, import json, and so on
NEVER, EVER, BE LAZY! IF YOU NEED TIME TO UNDERSTAND THE TASK TAKE YOUR TIME, BUT ALWAYS ANSWER PROPERLY WITH ALL THE USER REQUESTS

If you have to store data inside a database you MUST use the following action: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo. How to use the database:
- Based on the operation, you need to set True the following keys: add, update, find, find_one, delete.
- You need to specify the collection key.
- you need to specify the data key.
- If you need to query the database for an element, you have to specify the 'filter' key inside 'data'.
- If you want to update an element you need to specify the 'updateData' key.
- The only valid filter to update or delete is '_id'.
- Consider everthing between ``` an example:
        ```
        def main(args):
            if args.get('action') == 'create':
                data = {
                    "title": args.get('title'),
                    "author": args.get('author'),
                    "genre": args.get('genre'),
                    "published_year": args.get('published_year')
                }
                response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('action') == 'read':
                data = {"filter": args.get('filter')}
                response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('operation') == 'read_one':
                data = {
                    "title": args.get('title'),
                    "author": args.get('author'),
                    "genre": args.get('genre'),
                    "published_year": args.get('published_year')
                }
                response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find_one": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('action') == 'update':
                data = {"filter": args.get('filter'),
                    "updateData": {
                        "title": args.get('title'),
                        "author": args.get('author'),
                        "genre": args.get('genre'),
                        "published_year": args.get('published_year')
                    }
                }
                response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"update": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('action') == 'delete':
                data = {"filter": args.get('filter')}
                response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"delete": True, "collection": "books", "data": data})
                return {"body": response.text}
        ```
You can't use async.
If you need to accept parameters you will get those such as: args.get("url") to get "url", args.get("name") to get "name" and so on
You can use only the follow libraries: requests, re, json, BeatifulSoup. Remember to import the modules you use!
"""

messages = [
    {"role": "system", "content": ROLE}
]

def update_action(args):
    function = args.get('function', False)
    print(function)
    description = args.get('description', False)
    if not function and not description:
        return "error: data is missing"
    print("update")
    if USER['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{NAME}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={"exec":{"kind":"python:default", "code":function},})
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{USER['package']}/{NAME}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={"exec":{"kind":"python:default", "code":function},})
    requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "walkiria", "collection": USER['package'], "data": resp.json()})
    action = f"url: https://nuvolaris.dev/api/v1/web/gporchia/{USER['package']}/{NAME}\ndescription:{description}\nfunction:{function}\n\n"
    test = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/openai/tester', json={"input": action, "cookie": USER['cookie']})
    return test.text

def main(args):
    global USER
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    request = args.get('request', False)
    USER = args.get('user', False)
    if not request and not USER:
        return {"statusCode": 400}
    
    messages.append({"role": "user", "content": request})
    response = AI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=update_action_tool,
        tool_choice={"type": "function", "function": {"name": "update_action"}},
    )
    if response.choices[0].message.tool_calls:
        messages.append(response.choices[0].message)
        tool_calls = response.choices[0].message.tool_calls
        for tool_call in tool_calls:
            function_name = "update_action"
            function_to_call = update_action
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
                )
            print(function_response)
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })



update_action_tool = [
        {
            "type": "function",
            "function": {
                "name": "update_action",
                "description": "update action based on the request",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "object",
                            "properties": {
                                "function": {"type": "string", "description": "the function generated including the improvement suggested"},
                                "description": {"type": "string", "description": "updated description of the action"},
                            },
                            "required": ["function", "description"]
                        },
                    },
                    "required": ["args"]
                        
                }
            }
        }
]