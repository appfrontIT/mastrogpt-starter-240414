#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--param JWT_SECRET $JWT_SECRET
#--timeout 300000

import requests
from requests.auth import HTTPBasicAuth
import os
import json
import jwt
from openai import OpenAI

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
JWT = None
TOKEN = None
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

If you have to store data inside a database you MUST use the following action: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/{collection}/{operation}. How to use the database:
You need to fill collection and  operation.
Remember to set the path in the beginning of the code.
{operation} can be one of the following: 'find_one', 'find_many', 'add', 'add_many', 'delete', 'update'.
Here's an example using model 'Book', wiht fields: 'title', 'author', 'pages', 'year':
```python

    import requests
    import json

    def main(args):
        path = args.get('__ow_path', False)
        if not path:
            return {"statusCode": 500}
        
        # create an element using 'data'
        if path == '/create':
            response = request.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/add", json={"data": {"title": args.get("title"), "author": args.get("author"), "pages": args.get("pages"), "year": args.get("year")}})
            return {"statusCode": response.status_code, "body": response.text}
        
        # delete an element by id
        elif path == '/delete':
            response = request.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/delete?id=" + args.get('id'))
            return {"statusCode": response.status_code, "body": response.text}
        
        # update an element by id using 'data'
        elif path == '/update':
            response = request.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/update?id=" + args.get('id'), json={"data": {"title": args.get("title"), "author": args.get("author"), "pages": args.get("pages"), "year": args.get("year")}})
            return {"statusCode": response.status_code, "body": response.text}
        
        # find single element matching the filter
        elif path == '/find_one':
            response = request.get("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/find_one?title=" + args.get('title') + "&author=" args.get('author'))
            return {"statusCode": response.status_code, "body": response.text}
        
        # find all elements matching the filter
        elif path == '/find_many':
            response = request.get("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/find_many")
            return {"statusCode": response.status_code, "body": response.text}
        return {"statusCode": 400}
```
Try to use a path to identify the type of operation.
You can't use async.
Each parameters must be extracter using 'args.get('param')'. Example: args.get("url") to get "url", args.get("name") to get "name" and so on
You can use only the follow libraries: requests, re, json, BeatifulSoup. Remember to import the modules you use!
ALWAYS IMPORT requests, re, json, and any library you're going to use inside the function
"""

messages = [
    {"role": "system", "content": ROLE}
]

def deploy_action(name, function, description):
    global AI
    global JWT
    action_list = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1])).json()
    # Generate a new name if needed
    name_arr = ""
    for x in action_list:
        name_arr += (x['name']) + ", "
        if x['namespace'] == f"gporchia/{JWT['package']}" and x['name'] == name:
            messages = [
                {"role": "system", "content": f"Generate an unique name base on the description passed. Only 1 word is allowed. You can't use the following words to generate a name:\n\n{name_arr}"},
                {"role": "user", "content": description}
            ]
            name = AI.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            ).choices[0].message.content
            break
    url = f"https://nuvolaris.dev/api/v1/web/gporchia/{JWT['package']}/{name}"
    body = {
        "namespace": "gporchia/" + JWT['package'],
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
    if JWT['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{JWT['package']}/{name}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    if resp.status_code != 200:
        return False
    requests.post(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/walkiria/{JWT['package']}/add", json={"data": resp.json()})
    return f"""url: https://nuvolaris.dev/api/v1/web/gporchia/{JWT['package']}/{name}\ndescription: {description}\nfunction: {function}"""

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
    # if not action:
    #     return "there was an error generating the action, tell the user to try again"
    # if TEST:
    #     test_result = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), json={"action": action, "token": TOKEN})
    return action

def improve_action(args):
    function = args.get('function', False)
    description = args.get('description', False)
    if not function and not description:
        return "error: data is missing"
    if JWT['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{NAME}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={"exec":{"kind":"python:default", "code":function},})
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{JWT['package']}/{NAME}?overwrite=true", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json={"exec":{"kind":"python:default", "code":function},})
    requests.post(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/walkiria/{JWT['package']}", json={"data": resp.json()})
    action = f"url: https://nuvolaris.dev/api/v1/web/gporchia/{JWT['package']}/{NAME}\ndescription:{description}\nfunction:{function}\n\n"
    test = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]), json={"action": action, "token": JWT})
    return test.text

def main(args):
    global JWT
    global TEST
    global TOKEN
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    request = args.get('request', False)
    TOKEN = args.get('token', False)
    TEST = args.get('test', False)
    if not request or not TOKEN:
        return {"statusCode": 400}
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(TOKEN, key=secret, algorithms='HS256')
    messages.append({"role": "user", "content": request})
    response = AI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=create_action_tool,
        tool_choice={"type": "function", "function": {"name": "create_action"}},
    )
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
            openapi = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/openAPI',
                                    auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                                    json={'action': function_response, 'token': TOKEN})
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