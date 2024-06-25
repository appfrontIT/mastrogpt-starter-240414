#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action that create and test an action asynchronously"
#--param JWT_SECRET $JWT_SECRET
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/generate

import requests
from requests.auth import HTTPBasicAuth
import os
import json
import jwt
from openai import OpenAI
import urllib.parse

SESSION_USER = None
OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
JWT = None
TOKEN = None
NAME = ""
TEST = False
ROLE ="""
Your role is to create an action and verify it.
The available languages are: Python, Javascript, Go, Java, PHP.
Take your time to answer and you must procede step by step.
Actions must ALWAYS include the 'main' function, accepting '(args)' as parameters. This is mandatory.
Always return a JSON with keys 'body' and 'statusCode'. The body returned must always be a valid json, like: {'body': {<key>: <value>}}

NEVER, EVER, BE LAZY! IF YOU NEED TIME TO UNDERSTAND THE TASK TAKE YOUR TIME, BUT ALWAYS ANSWER PROPERLY WITH ALL THE USER REQUESTS

Mandatory:
    1 - import the modules you use in the function.
    2 - Always include authorizations in your code. Example in python:
        def main(args):
            token = args['__ow_headers'].get('authorization', False)
            if not token:
                return {'statusCode': 401}

    3 - If you have to store data inside a database you MUST use the following action: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/{collection}/{operation}.
        Never opens Mongo client inside your functions, always use the API.
        How to use the database:
        You need to fill collection and operation.
        Remember to set the path in the beginning of the code.
        {operation} can be one of the following: 'find_one', 'find_many', 'add', 'add_many', 'delete', 'update'.
        Here's an example using Python, with model 'Book', wiht fields: 'title', 'author', 'pages', 'year':
        ```python

            import requests
            import json

            def main(args):
            
                # check for authorization token
                token = args['__ow_headers'].get('authorization', False)
                if not token:
                    return {'statusCode': 401}
                path = args.get('__ow_path', False)
                if not path:
                    return {"statusCode": 500}

                # create an element using 'data'
                if path == '/create':
                    response = request.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/add", headers = {"Authorization": token}, json={"data": {"title": args.get("title"), "author": args.get("author"), "pages": args.get("pages"), "year": args.get("year")}})
                    return {"statusCode": response.status_code, "body": response.json()}

                # delete an element by id
                elif path == '/delete':
                    response = request.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/delete?id=" + args.get('id'), headers = {"Authorization": token},)
                    return {"statusCode": response.status_code, "body": response.json()}

                # update an element by id using 'data'
                elif path == '/update':
                    response = request.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/update?id=" + args.get('id'), headers = {"Authorization": token}, json={"data": {"title": args.get("title"), "author": args.get("author"), "pages": args.get("pages"), "year": args.get("year")}})
                    return {"statusCode": response.status_code, "body": response.json()}

                # find single element matching the filter
                elif path == '/find_one':
                    response = request.get("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/find_one?title=" + args.get('title') + "&author=" args.get('author'), headers = {"Authorization": token},)
                    return {"statusCode": response.status_code, "body": response.json()}

                # find all elements matching the filter
                elif path == '/find_many':
                    response = request.get("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/books/find_many", headers = {"Authorization": token},)
                    return {"statusCode": response.status_code, "body": response.json()}
                return {"statusCode": 400}
        ```

    4 - Each parameters must be extracter using 'args.get('param')'. Example: args.get("url") to get "url", args.get("name") to get "name" and so on
    5 - You MUST import any library or module you use in the action.
    6 - Pay attention to utilize the same language through all the code! Don't mix language, is bad and you're not stupid!
    7 - It's very important that you fill your code with comments, in a way the user will be able to understand what you are doing and can perform some modifications
    8 - NEVER use async, but you can return a promise. 
    9 - axios, jsdom, node-html-parser are forbidden, you can't use them
"""

def deploy_action(name, function, description, language, returns = None):
    global AI
    global JWT
    global SESSION_USER
    package = SESSION_USER['username']
    package_up = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/packages/{package}", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    if package_up.status_code != 200:
        return {'error: package not found'}
    action_list = package_up.json()['actions']
    # Generate a new name if needed
    
    name_arr = []
    for x in action_list:
        name_arr.append(x['name'])
    if name in name_arr:
        messages = [
            {"role": "system", "content": f"Generate an unique name base on the description passed. Only 1 word is allowed. You can't use the following words to generate a name:\n\n{name_arr}"},
            {"role": "user", "content": description}
        ]
        name = AI.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        ).choices[0].message.content
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': SESSION_USER['_id'], 'message': {'output': "Ho creato l'azione, procedo a verificarla"}})
    verify = AI.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": ROLE},
            {"role": "user", "content": f"""Analyze the correctness of the following function and improve it with your suggestion. You must answer with a valid JSON as follow (fill the fields between -): {{'function': -function-, 'description': -description-}}.
            Think backwards and elaborate the function output between yourself before producing an answer. Take your time to answer. Function:\n{function}.\nIf needed, update the following description:\n{description}"""}
        ],
        response_format={"type": "json_object"},
    ).choices[0].message.content
    verify = json.loads(verify)
    function = verify['function']
    description = verify['description']
    editor = {"function": function, "description": description, "name": name, "namespace": SESSION_USER['namespace'], "package": SESSION_USER['package'][0], "language": language}
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': SESSION_USER['_id'], 'message': {'output': "l'azione é stata verifica, adesso procedo con il deploy", 'editor': editor}})
    deploy = requests.put('https://nuvolaris.dev/api/v1/web/gporchia/base/action/add',
                headers={"Authorization": "Bearer " + SESSION_USER['JWT']},
                json={
                    "name": name,
                    "function": function,
                    "description": description,
                    "namespace":  "gporchia/" + SESSION_USER['username'],
                    "package": SESSION_USER['username'],
                    "language": language,
                    "returns": json.dumps(returns)
                })
    if deploy.ok:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': SESSION_USER['_id'], 'message': {'output': "Deploy avvenuto correttamente"}})
    else:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': SESSION_USER['_id'], 'message': {'output': "C'é stato un problema nel deployare la tua azione"}})
        return "C'é stato un problema nel deployare l'azione"
    # requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/code_editor/add", json={'editor': editor}, headers={'cookie': f"appfront-sess-cookie={SESSION_USER['cookie']}"})
    return f"""url: https://nuvolaris.dev/api/v1/web/gporchia/{package}/{name}\ndescription: {description}\nfunction: {function}"""

def create_action(args):
    global NAME
    NAME = args.get('name', False)
    function = args.get('function', False)
    language = args.get('language', False)
    function = function.replace('```', '')
    function = function.replace(language, '')
    function = function.replace(language, '')
    description = args.get('description', False)
    return deploy_action(NAME, function, description, language, args.get('return'))

def main(args):
    global JWT
    global TOKEN
    global SESSION_USER
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    request = args.get('request', False)
    TOKEN = args.get('token', False)
    if not request or not TOKEN:
        return {"statusCode": 400}
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(TOKEN, key=secret, algorithms='HS256')
    response = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?filter=" + urllib.parse.quote(json.dumps({'JWT': TOKEN})), headers={'Authorization': f"Bearer {TOKEN}"})
    if response.status_code != 200:
        return {"statusCode": 404}
    SESSION_USER = response.json()
    messages = [
        {"role": "system", "content": ROLE},
        {"role": "user", "content": request}
    ]
    response = AI.chat.completions.create(
        model="gpt-4o",
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
                            "description": {"type": "string", "description": "a description of the action you made. The description MUST includes the parameters the action needs such as: {key: type, key: type, ...}. Example: 'an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}, None'."},
                            "language": {"type": "string", "description": "the language in which you wrote the function. It must be 1 word from the following: 'python', 'javascript', 'go', 'php'"},
                            "return": {
                                "type": "array",
                                "description": "an array of each possible return of the action. Example: [{'status': 200, 'body': body}, {'status': 204}, {'status': 401, 'body': 'authorization failed'}, {...}]",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "content": "the return status code"},
                                        "body": {"type": "string", "content": "the return body, if present"}
                                    },
                                    "required": ["status"]
                                },
                                },
                            },
                        },
                    },
                    "required": ["args"]
                },
            },
        },
        ]