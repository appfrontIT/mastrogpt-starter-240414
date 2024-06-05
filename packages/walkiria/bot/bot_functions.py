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
        status = utils.action_info(action['name'], action['package'])
        if status.status_code == 200:
            obj = status.json()
            action_array += f"name: {obj['name']}\n"
            annotations = obj['annotations']
            for pair in annotations:
                if pair['key'] == 'url' or pair['key'] == 'description':
                    action_array += f"{pair['key']}: {pair['value']}\n"
            action_array += f"code: {obj['exec']['code']}\n"
        else:
            return f"the following action does not exists: {action}\n"
    if action_array != "":
        query = f"{description}\nHere the informations about the actions you have to call inside it: {action_array}"
    else:
        query = description
    html = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/html_gen/bot", json={"input": query})
    if html.status_code == 204:
        return "failed to generate the HTML"
    output = html.json()
    ret = {"body": output.get("output")}
    function = f"""def main(args):\n\treturn {ret}"""
    editor = {"function": output, "description": description, "name": name, "namespace": config.session_user['namespace'], "package": config.session_user['username'], "language": 'html'}
    deploy = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/base/action/add",
                        headers={"Content-Type": "application/json", "Authorization": "Bearer " + config.session_user['JWT']},
                        json={
                            "name": editor['name'],
                            "function": function,
                            "description": description,
                            "namespace": config.session_user['namespace'],
                            "package": config.session_user['username'],
                            "language": 'python'})
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': {'editor': editor}})
    return f"Everything is fine, don't call any other function"

def update_action(function = False, fix = False):
    if function and fix:
        query = f"apply this fix to the following function.\nfix: {fix}\n\nfunction:{function}"
        response = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/generate?blocking=true',
                            auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                            json={"request": query, "token": config.session_user['JWT']})
        return response.text
    return "there was an error performing this operation"

def create_action(query):
    response = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/generate?blocking=true',
                            auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                            json={"request": query, "token": config.session_user['JWT']})
    return response.text

def db_store(url, collection, format):
    return requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/db_store_init', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "url": url,
        "collection": collection,
        "format": format,
        "user": config.session_user
    }).text

def action_info(name = False, package = False):
    if not name or not package:
        return "Ho bisogno sia del nome che del package per recuperare l'azione"
    if package not in config.session_user['package'] and config.session_user['role'] != 'admin':
        return "Non sei autorizzato ad accedere a questa azione"
    action = utils.action_info(name, package)
    if action.status_code == 200:
        obj = action.json()
        for an in obj['annotations']:
            if an['key'] == 'description':
                namespace = obj['namespace']
                editor = {"function": obj['exec']['code'], "name": obj['name'], "description": an['value'], "namespace": namespace.split('/')[0], "package": package, "language": obj['exec']['kind'].split(':')[0]}
                requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/code_editor/add", json={'editor': editor}, headers={"cookie": f"cookie={config.session_user['cookie']}"})
                break
        return f"""Display the following fields of the passed action: description, parameters, curl example with the full url without alias, action URL with full url.\nAction:\n{action.json()}"""
    return "Non sono riuscito a trovare l'azione richiesta. Assicurati che il nome sia corretto e che sia specificato il package se appartiene ad uno"

def delete_action(name = False, package = False):
    if not name or not package:
        return "Ho bisogno del nome e del package per eliminare l'azione"
    if package not in config.session_user['package'] and config.session_user['role'] != 'admin':
        return "Non sei autorizzato ad accedere a questa azione"
    response = utils.delete_action(name, package)
    delete = requests.delete('https://nuvolaris.dev/api/v1/web/gporchia/base/openAPI/delete',
            headers={'Authorization': 'Bearer ' + config.session_user['JWT']},
            json={'action': f"""url: https://nuvolaris.dev/api/v1/web/gporchia/{package}/{name}"""})
    return f"status: {response.status_code}, body: {response.json()}"

def show_all_actions():
    actions_list = utils.get_actions().json()
    action_arr = []
    for action in actions_list:
        if config.session_user['role'] == 'admin':
            action_arr.append(action)
        else:
            package = action['namespace'].split('/')[1]
            if package in config.session_user['package']:
                action_arr.append(action)
    name_arr = []
    for x in action_arr:
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
    return f"""display all the following actions.\nActions:\n{name_arr}\nYou must display the actions in this output: namespace: <namespace>\nname: <name>\ndescription; <description>"""

def tools_func(
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], "message": {"output": "Certo, procedo subito con la tua richiesta"}})
    messages.append(response.choices[0].message)
    for tool_call in tool_calls:
        print(tool_call.function.name)
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            **function_args
            )
        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response
        })
        requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                    auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                    json={'id': config.session_user['_id'], "message": {"output": "Ho eseguito l'operazione, sto elaborando una risposta"}}
                    )
    return config.AI.chat.completions.create(model=MODEL, messages=messages,).choices[0].message.content


available_functions = {
    "show_all_actions": show_all_actions,
    "delete_action": delete_action,
    "update_action": update_action,
    "action_info": action_info,
    "create_action": create_action,
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
            "name": "update_action",
            "description": """You must update the provided code according to the user request""",
            "parameters": {
                "type": "object",
                "properties": {
                    "function": {"type": "string", "description": "the full function code"},
                    "fix": {"type": "string", "description": "one or more fix to apply on the code"}
                    },
                "required": ["function", "fix"],
                },
            }
        },
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
            "name": "delete_action",
            "description": "the user wants to delete an action",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "the action name to be deleted"},
                    "package": {"type": "string", "description": "the action package"}
                    },
                    "required": ["name", "package"],
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "action_info",
            "description": "the user wants information about an action or how to use it",
            "parameters": {
                "type": "object",
                "properties": {
                    "name" : {"type": "string", "description": "the name of the action, it must be 1 word"},
                    'package': {"type": "string", "description": "the package of the action"}
                    },
                    "required": ["name", "package"],
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
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "action name"},
                                        "package": {"type": "string", "description": "the package of the action"}
                                    }
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