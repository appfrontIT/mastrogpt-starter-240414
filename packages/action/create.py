#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
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
TEST = False
ROLE ="""
Your role is to create an action and test it. If the tester suggests improvements you must implement them and test again. If all tests are passed, don't call any function.
You only code in Python.
Take your time to answer and you must procede step by step.
Function ALWAYS start with "def main(args):".
The return is always: {"body": string}. Example: '{"body": text}', '{"body": response.text}.
NEVER, EVER, BE LAZY! IF YOU NEED TIME TO UNDERSTAND THE TASK TAKE YOUR TIME, BUT ALWAYS ANSWER PROPERLY WITH ALL THE USER REQUESTS

Mandatory: import the modules you use in the function.

If you have to store data inside a database you MUST use the following action: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo. How to use the database:
- Based on the operation, you need to set True the following keys: add, update, find, find_one, delete.
- You need to specify the collection key.
- you need to specify the data key.
- If you need to query the database for an element, you have to specify the 'filter' key inside 'data'.
- If you want to update an element you need to specify the 'updateData' key.
- The only valid filter to update or delete is '_id'.
- Consider everthing between ``` an example:
        ```
        import json
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
ALWAYS IMPORT requests, re, json, and any library you're going to use inside the function
"""

messages = [
    {"role": "system", "content": ROLE}
]

def deploy_action(name, function, description):
    global AI
    action_list = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1])).json()
    # Generate a new name if needed
    name_arr = ""
    for x in action_list:
        name_arr += (x['name']) + ", "
        if x['namespace'] == f"gporchia/{USER['package']}" and x['name'] == name:
            messages = [
                {"role": "system", "content": f"Generate an unique name base on the description passed. Only 1 word is allowed. You can't use the following words to generate a name:\n\n{name_arr}"},
                {"role": "user", "content": description}
            ]
            name = AI.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            ).choices[0].message.content
            break
    url = f"https://nuvolaris.dev/api/v1/web/gporchia/{USER['package']}/{name}"
    body = {
        "namespace": "gporchia/" + USER['package'],
        "name": name,
        "exec":{"kind":"python:default", "code":function},
        "annotations":[
            {"key":"web-export", "value":True},
            {"key":"raw-http","value":False},
            {"key": "final", "value": True},
            {"key": "description", "value": description},
            {"key": "url", "value": url}
            ]
        }
    if USER['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{USER['package']}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    if resp.status_code != 200:
        return False
    requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "walkiria", "collection": USER['package'], "data": resp.json()})
    return f"url:'https://nuvolaris.dev/api/v1/web/gporchia/{USER['package']}/{name}', description:'description', function:'function'"

def create_action(args):
    global NAME
    global TEST
    NAME = args.get('name', False)
    function = args.get('function', False)
    function = function.replace('```', '')
    function = function.replace('python', '')
    function = function.replace('Python', '')
    description = args.get('description', False)
    action = deploy_action(NAME, function, description)
    if not action:
        return "there was an error generating the action, tell the user to try again"
    if TEST:
        test_result = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), json={"input": action, "cookie": USER['cookie']})
    return action

def improve_action(args):
    function = args.get('function', False)
    description = args.get('description', False)
    if not function and not description:
        return "error: data is missing"
    if USER['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{NAME}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={"exec":{"kind":"python:default", "code":function},})
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{USER['package']}/{NAME}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={"exec":{"kind":"python:default", "code":function},})
    requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "walkiria", "collection": USER['package'], "data": resp.json()})
    action = f"url: https://nuvolaris.dev/api/v1/web/gporchia/{USER['package']}/{NAME}\ndescription:{description}\nfunction:{function}\n\n"
    test = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), json={"input": action, "cookie": USER['cookie']})
    return test.text

def main(args):
    global USER
    global TEST
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    request = args.get('request', False)
    USER = args.get('user', False)
    TEST = args.get('test', False)
    if not request or not USER:
        return {"statusCode": 400}
    
    messages.append({"role": "user", "content": request})
    response = AI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=create_action_tool,
        tool_choice={"type": "function", "function": {"name": "create_action"}},
    )
    print(response.choices[0])
    if response.choices[0].message.tool_calls:
        tool_calls = response.choices[0].message.tool_calls
        for tool_call in tool_calls:
            function_name = "create_action"
            function_to_call = create_action
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
                )
            # messages.append({
            #     "tool_call_id": tool_call.id,
            #     "role": "tool",
            #     "name": function_name,
            #     "content": function_response
            # })
            return {"body": function_response}
    print('no tool')
    return {"body": response.choices[0].message.content}


create_action_tool = [{
        "type": "function",
        "function": {
            "name": "create_action",
            "description": "the user asks to create an action NOT returning HTML. If the action returns html use html_gen instead",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "action name"},
                            "function": {"type": "string", "description": "the generated function. It must starts with 'def main(args):'"},
                            "description": {"type": "string", "description": "a description of the action you made. The description MUST includes the parameters the action needs such as: {key: type, key: type, ...}. Example: 'an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}, None'"},
                            },
                        },
                    },
                    "required": ["args"]
                },
            },
        },]

improve_action_tool = [
        {
            "type": "function",
            "function": {
                "name": "improve_action",
                "description": "the tester suggests some improvement to the action",
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