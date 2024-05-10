from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
from bs4 import BeautifulSoup
import requests
import os
from requests.auth import HTTPBasicAuth
import json
import config, utils
from chart import grapher
from tester import tester

MODEL="gpt-3.5-turbo"

def crawler(url = '', embedding = False):
    if url == '':
        return "No url provided"
    resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/utility/apify_scraper", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={"url": url, "embedding": embedding})
    return resp.text

def html_gen(args):
    actions_info = args.get('actions_names', '')
    description: str = args.get('description', '')
    name: str = args.get('name', '')
    action_array = ""
    for action in actions_info:
        status = utils.action_info(config.session_user['package'], action)
        obj = json.loads(status)
        error = obj.get('error', '')
        if error != '':
            return f"the following action does not exists: {action}\n"
        action_array += f"name: {obj['name']}\n"
        annotations = obj['annotations']
        for pair in annotations:
            if pair['key'] == 'url' or pair['key'] == 'description':
                action_array += f"{pair['key']}: {pair['value']}\n"
        action_array += f"code: {obj['exec']['code']}\n"
    if action_array != "":
        query = f"{description}\nHere the informations about the actions you have to call inside it: {action_array}"
    else:
        query = description
    html = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/html_gen/create", json={"input": query})
    html_obj = html.json()
    output = html_obj.get('output', '')
    if output == '':
        return "failed to generate the HTML"
    ret = {"body": output}
    function = f"""def main(args):\n\treturn {ret}"""
    action = deploy_action(name, function, description)
    # test = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={"input": action, "cookie": config.session_user['cookie']})
    return f"{action}\nEverything is fine, don't call any other function"

def update_action(name, modifications):
    action_list = utils.get_actions()
    obj = json.loads(action_list)
    name_arr = []
    for x in obj:
        name_arr.append(x['name'])
    if name in name_arr:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], 'message': {"output": f"updating action '{name}', please wait"}})
        action = utils.action_info(config.session_user['package'], name)
        messages = [
            {"role": "system", "content": """You only answer in JSON format. You need to provide the following keys for the user: "function", "description". Apply the user modifications to the action provided. function ALWAYS start with "def main(args):".
            Example: '{"function": "the function you generated based on the modifications asked", "description": "a description of the functions with the parameters needed. Example: 'description of function. Parameters: {'arg1': type, 'arg2': type}'"}'"""},
            {"role": "user", "content": f"{modifications}, Action to modify:\n{action}\nYou need to modify the function inside the action. Take your time to answer"}
            ]
        response = config.AI.chat.completions.create(
                model=MODEL,
                messages=messages
            )
        utils.delete_action(config.session_user['package'], name)
        comp = response.choices[0].message.content
        obj = json.loads(comp)
        config.html += "<h1>UPDATE:</h1><br />"
        action = deploy_action(name, obj['function'], obj['description'])
        test = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={"input": action, "cookie": config.session_user['cookie']})
        return test.text
    return f"No action with that name exists, here a list of existing actions:\n{show_all_actions()}"

def deploy_action(name, function, description):
    action_list = utils.get_actions()
    obj = json.loads(action_list)
    # Generate a new name if needed
    name_arr = ""
    for x in obj:
        name_arr += (x['name']) + ", "
        if x['namespace'] == f"gporchia/{config.session_user['package']}" and x['name'] == name:
            messages = [
                {"role": "system", "content": f"Generate an unique name base on the description passed. Only 1 word is allowed. You can't use the following words to generate a name:\n\n{name_arr}"},
                {"role": "user", "content": description}
            ]
            name = config.AI.chat.completions.create(
                model=MODEL,
                messages=messages
            ).choices[0].message.content
            break
    function = function.replace('```', '')
    function = function.replace('python', '')
    function = function.replace('Python', '')
    url = f"https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}"
    body = {
        "namespace": config.session_user['namespace'] + "/" + config.session_user['package'],
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
    if config.session_user['role'] == "admin":
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}?overwrite=true", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    else:
        resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{config.session_user['package']}/{name}?overwrite=true", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), headers={"Content-type": "application/json"}, json=body)
    print(resp.text)
    if resp.status_code != 200:
        return resp.text
    requests.post(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/walkiria/{config.session_user['package']}/add", json={"data": resp.json()})
    # config.html += f"""
    #     <head>
    #     <link rel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/styles/default.min.css">
    #         <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/highlight.min.js"></script>
    #         <script>hljs.initHighlightingOnLoad();</script>
    #         <h3>ACTION URL:<br><a href="https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}" target="_blank">https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}</a></h3>
    #     </head>
    #     <body>
    #         <pre><code class="python"><xmp>{function}</xmp></code></pre>
    #     </body>
    #     \n\n
    #     """
    return f"url: https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}\ndescription:{description}\nfunction:{function}\n\n"

def create_action(request):
    response = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/action/create', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={"request": request, "user": config.session_user, "test": True})
    return "the action is in production and it will tested as well"

def db_store(url, collection, format):
    print(collection)
    return requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/db_store_init', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "url": url,
        "collection": collection,
        "format": format,
        "user": config.session_user
    }).text

def action_info(name):
    action_list = utils.get_actions()
    obj = json.loads(action_list)
    name_arr = []
    for x in obj:
        name_arr.append(x['name'])
    if name in name_arr:
        status = utils.action_info(config.session_user['package'], name)
        obj = json.loads(status)
        config.html = f"<html><body><pre><code><xmp>{json.dumps(obj, indent=2)}</xmp></code></pre></code></html>"
        if len(status) > 8000:
            description = ""
            for x in obj['annotations']:
                if x['key'] == 'description':
                    description = x['value']
                    break
            if description != "":
                return description
            else:
                return status[:8000]
        return f"""The action url is EXACTLY this: https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}. ALWAYS USE THE FULL URL. Fill everythin between ``:
        - **Description**: `put description here`
        - **Parameters**: `put parameters here`
        - **Code**: `put python code example that use the action`
        - **Curl**: `put curl request example to the action`
        - **Action URL**: `put the action url here`
        Action:\n{status}"""
    return f""""The action you requested does not exists. Here is a list of available actions:\n{name_arr}
    """

def delete_action(name_array):
    to_obj = []
    for el in name_array:
        status = utils.delete_action(config.session_user['package'], el)
        to_obj.append(json.loads(status))
    config.html = f"<html><body><pre><code><xmp>{json.dumps(to_obj, indent=2)}</xmp></code></pre></code></html>"
    return status

def show_all_actions():
    status = utils.get_actions()
    obj = json.loads(status)
    name_arr = ""
    for x in obj:
        if x['namespace'] != config.session_user['namespace']:
            continue
        name_arr += f"Action:{x['namespace']}/{x['name']}"
        annotations = x['annotations']
        description = ""
        for an in annotations:
            if an['key'] == 'description':
                description = an['value']
                name_arr += f"\nDescription:{description}\n"
                break
    if len(name_arr) == 0:
        return "tell the user there's no action under his package"
    config.html = f"<html><body><pre><code><xmp>{json.dumps(obj, indent=2)}</xmp></code></pre></code></html>"
    return f"""display each actions with the description.
    Actions:\n{name_arr}"""

def tools_func(
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], "message": {"output": "Sure, I'll get to work on it right away!"}})
    messages.append(response.choices[0].message)
    for tool_call in tool_calls:
        print(tool_call.function.name)
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            **function_args
            )
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'cookie': config.session_user['cookie'], "message": {"output": "I've elaborated the data, let me generate an answer"}})
        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response
        })
    return config.AI.chat.completions.create(model=MODEL, messages=messages,).choices[0].message.content


available_functions = {
    "show_all_actions": show_all_actions,
    "delete_action": delete_action,
    "action_info": action_info,
    "create_action": create_action,
    "update_action": update_action,
    "html_gen": html_gen,
    "crawler": crawler,
    "tester": tester,
    "grapher": grapher,
    "db_store": db_store,
}

tools = [
        {
        "type": "function",
        "function": {
            "name": "show_all_actions",
            "description": """the user want to display or list all the actions""",
            "parameters": {
                "type": "object",
                "properties": {},
                    "required": [],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "create_action",
            "description": "the user wants to create an action. Redirect the user request to the correct API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "the user request"},
                    },
                    "required": ["request"]
                },
            },
        },
        {
        "type": "function",
        "function": {
            "name": "update_action",
            "description": "improve, update or modify an action",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "action name"},
                    "modifications": {"type": "string", "description": "the user requested modifications"},
                    },
                    "required": ["name", "modifications"],
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "delete_action",
            "description": "the user wants to delete an action",
            "parameters": {
                "type": "object",
                "properties": {
                    "name_array": {
                        "type": "array",
                        "description": "the name of the actions to be deleted",
                        "items": {
                            "type": "string"
                            }
                        },
                    },
                    "required": ["name_array"],
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "action_info",
            "description": "the user wnats information about an action or how to use it",
            "parameters": {
                "type": "object",
                "properties": {
                    "name" : {"type": "string", "description": "the name of the action, it must be 1 word"}
                },
                    "required": ["name"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "html_gen",
            "description": "the user asks to create an action returning HTML, or the user wants an HTML page. Example: 'create an action returning an html page...', 'create an html ...', and so on",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "action name"},
                            "description": {"type": "string", "description": "detailed description of the action to create"},
                            "actions_names": {
                                "type": "array",
                                "description": "Array of the actions name to be called inside the HTML. If no actions provided, return an empty array",
                                "items": {
                                    "type": "string",
                                    }
                                },
                            },
                            "required": ["name", "description", "actions_names"]
                        },
                    },
                    "required": ["args"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "crawler",
            "description": "the user wants information about a web page or explicity ask to crawl a web page. Don't call this action if the user wants to store data inside the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "the url to crawl"},
                    "embedding": {"type": "boolean", "description": "True in case the user asks to embed data of the url, False otherwise"}
                    },
                    "required": ["url", "embedding"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "tester",
            "description": "the user wants to test an action giving the name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "the action name to test"},
                    },
                    "required": ["name"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "grapher",
            "description": "the user wants to generate a graph or chart",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "the user specific request"},
                    "name": {"type": "string", "description": "name of the action to generate. it must ends with '_chart'"},
                    "description": {"type": "string", "description": "a short description of the chart"},
                    "type": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string", "description": "data to visualize inside the chart"},
                            "collection": {"type": "string", "description": "the collection where to get the data from"},
                            }
                        }
                    },
                    "required": ["request", "name", "description", "type"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "db_store",
            "description": "the user gives wants to store data inside the database from an url",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "the url of the file to store in the database"},
                    "collection": {"type": "string", "description": "the collection where to store the data inside the database in snake_case. This should't include the 'collection' prefix"},
                    "format": {"type": "string", "description": "how the data must be stored in pair of key value. Must be in markdown format"},
                    },
                    "required": ["url", "collection", "format"]
                }
            }
        }
]