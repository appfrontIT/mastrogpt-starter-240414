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
        if status.status_code == 200:
            obj = status.json()
            action_array += f"name: {obj['name']}\n"
            annotations = obj['annotations']
            for pair in annotations:
                if pair['key'] == 'url' or pair['key'] == 'description':
                    action_array += f"{pair['key']}: {pair['value']}\n"
            action_array += f"code: {obj['exec']['code']}\n"
        return f"the following action does not exists: {action}\n"
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
    return f"{action}\nEverything is fine, don't call any other function"

def update_action(name, modifications):
    action_list = utils.get_actions()
    name_arr = []
    for x in action_list.json():
        name_arr.append(x['name'])
    if name in name_arr:
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': str(config.session_user['_id']), 'message': {"output": f"updating action '{name}', please wait"}})
        action = utils.action_info(config.session_user['package'], name)
        messages = [
            {"role": "system", "content": """You only answer in JSON format. You need to provide the following keys for the user: "name", "function", "description". Apply the user modifications to the action provided. function ALWAYS start with "def main(args):".
            Example: '{"name": "the action name", "function": "the function you generated based on the modifications asked", "description": "a description of the functions with the parameters needed. Example: 'description of function. Parameters: {'arg1': type, 'arg2': type}'"}'"""},
            {"role": "user", "content": f"{modifications}, Action to modify:\n{action.text}\nYou need to modify the function inside the action. Take your time to answer"}
            ]
        response = config.AI.chat.completions.create(
                model=MODEL,
                messages=messages
            )
        utils.delete_action(name, config.session_user['package'])
        comp = response.choices[0].message.content
        obj = json.loads(comp)
        config.html += "<h1>UPDATE:</h1><br />"
        action = deploy_action(name, obj['function'], obj['description'])
        test = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={"input": action, "token": str(config.session_user['JWT'])})
        return test.text
    return f"No action with that name exists, here a list of existing actions:\n{show_all_actions()}"

def deploy_action(name, function, description):
    action_list = utils.get_actions()
    obj = action_list.json()
    name_arr = []
    for x in obj:
        name_arr.append({'name': x['name'], 'namespace': x['namespace']})
    for x in name_arr:
        if x['namespace'] == f"gporchia/{config.session_user['package']}" and x['name'] == name:
            messages = [
                {"role": "system", "content": f"Generate an unique name base on the description passed. Only 1 word is allowed. You can't use the following words to generate a name:\n\n{json.dumps(name_arr)}"},
                {"role": "user", "content": description}
            ]
            name = config.AI.chat.completions.create(model=MODEL, messages=messages).choices[0].message.content
            break
    function = function.replace('```', '')
    function = function.replace('python', '')
    function = function.replace('Python', '')
    response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/default/action/add',
                            headers={'Authorization': 'Bearer ' + config.session_user['JWT']},
                            json={'name': name, 'function': function, 'description': description})
    if response.status_code == 200:
        requests.post(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/walkiria/{config.session_user['package']}/add", json={"data": response.json()})
        return f"url: https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}\ndescription:{description}\nfunction:{function}\n\n"
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
    return f"statusCode: {response.status_code}, body: {response.text}"

def create_action(query):
    response = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/generate?blocking=true',
                            auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                            json={"request": query, "token": config.session_user['JWT'], "test": True})
    return response.text

def db_store(url, collection, format):
    return requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/db_store_init', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "url": url,
        "collection": collection,
        "format": format,
        "user": config.session_user
    }).text

def action_info(name, package = None):
    if not package:
        action = utils.action_info(name)
    else:
        action = utils.action_info(name, package)
    if action.status_code == 200:
        obj = action.json()
        for an in obj['annotations']:
            if an['key'] == 'description':
                namespace = obj['namespace']
                editor = {"function": obj['exec']['code'], "name": obj['name'], "description": an['value'], "namespace": namespace.split('/')[0], "package": package}
                requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/code_editor/add", json={'editor': editor}, headers={"cookie": f"cookie={config.session_user['cookie']}"})
                break
        return f"""Display the following fields of the passed action: description, parameters, curl example with the full url without alias, action URL with full url.\nAction:\n{action.json()}"""
    return "Non sono riuscito a trovare l'azione richiesta. Assicurati che il nome sia corretto e che sia specificato il package se appartiene ad uno"

def delete_action(name_array):
    response = requests.get('https://nuvolaris.dev/api/v1/web/gporchia/default/action/delete', params={'actions': name_array}, headers={'Authorization': 'Bearer ' + config.session_user['JWT']})
    return f"status: {response.status_code}, body: {response.json()}"

def show_all_actions():
    response = requests.get('https://nuvolaris.dev/api/v1/web/gporchia/default/action/find_all', headers={'Authorization': 'Bearer ' + config.session_user['JWT']})
    if response.status_code != 200:
        return "tell the user there's no action under his package"
    name_arr = []
    for x in response.json():
        if x['namespace'] != config.session_user['namespace'] and config.session_user['role'] != 'admin':
            continue
        x.pop('limits')
        x.pop('publish')
        x.pop('updated')
        x.pop('version')
        x.pop('exec')
        annotations = []
        for an in x['annotations']:
            if an['key'] == 'description' or an['key'] == 'url':
                annotations.append(an)
        x['annotations'] = annotations
        name_arr.append(x)
    config.html = f"<html><body><pre><code><xmp>{json.dumps(name_arr, indent=2)}</xmp></code></pre></code></html>"
    return f"""display each actions with the description.\nActions:\n{name_arr}\nYou must display the actions in this output: namespace: <namespace>\nname: <name>\ndescription; <description>"""

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
            "description": "generate an action based on user informations. Call this only when you have enought data to generate an action",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "all the informations about the action to create"},
                },
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
                    "name" : {"type": "string", "description": "the name of the action, it must be 1 word"},
                    'package': {"type": "string", "description": "the package of the action"}
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
                    'package': {"type": "string", "description": "the package of the action"}
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