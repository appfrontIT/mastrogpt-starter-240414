from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
from bs4 import BeautifulSoup
import requests
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import utils
import config
import bot_functions

MODEL="gpt-3.5-turbo"
CLIENT = None

def html_gen(args):
    actions_info = args.get('actions_info', '')
    description: str = args.get('description', '')
    name: str = args.get('name', '')
    action_array = ""
    for action in actions_info:
        status = utils.action_info(action)
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
    html = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/openai/html_gen", json={"input": query})
    html_obj = html.json()
    output = html_obj.get('output', '')
    if output == '':
        return "failed to generate the HTML"
    ret = {"body": output}
    actions = []
    function = f"""def main(args):\n\treturn {ret}"""
    actions.append({"description": description, "name": name, "function": function})
    return create_action(actions)

def update_action(name, modifications):
    action_list = utils.get_actions()
    print(modifications)
    obj = json.loads(action_list)
    name_arr = []
    for x in obj:
        name_arr.append(x['name'])
    if name in name_arr:
        action = utils.action_info(config.package, name)
        messages = [
            {"role": "system", "content": """You only answer in JSON format. You need to provide the following keys for the user: "function", "description". Apply the user modifications to the action provided. function ALWAYS start with "def main(args):".
            Example: '{"function": "the function you generated based on the modifications asked", "description": "a description of the functions with the parameters needed. Example: 'description of function. Parameters: {'arg1': type, 'arg2': type}'"}'"""},
            {"role": "user", "content": f"{modifications}, Action to modify:\n{action}\nYou need to modify the function inside the action. Take your time to answer"}
            ]
        response = CLIENT.chat.completions.create(
                model=MODEL,
                messages=messages
            )
        utils.delete_action(config.package, name)
        comp = response.choices[0].message.content
        print(comp)
        obj = json.loads(comp)
        action = deploy_action(name, obj['function'], obj['description'])
        test = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/openai/tester', json={"input": action})
        print(test.text)
        return test.text
    return f"No action with that name exists, here a list of existing actions:\n{show_all_actions()}"

def deploy_action(name, function, description):
    action_list = utils.get_actions()
    obj = json.loads(action_list)
    name_arr = []
    # Generate a new name if needed
    for x in obj:
        name_arr.append(x['name'])
    if name in name_arr:
        print("name already exists")
        messages = [
            {"role": "system", "content": f"Generate an unique name base on the description passed. Only 1 word is allowed. You can't use the following words to generate a name:\n\n{name_arr}"},
            {"role": "user", "content": description}
        ]
        name = CLIENT.chat.completions.create(
            model=MODEL,
            messages=messages
        ).choices[0].message.content
    config.html = ""
    function = function.replace('```', '')
    function = function.replace('python', '')
    function = function.replace('Python', '')
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    url = f'https://nuvolaris.dev/api/v1/web/gporchia/{config.package}/{name}'
    body = {
        "namespace": config.namespace,
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
    resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{config.package}/{name}?overwrite=true", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
    if resp.status_code != 200:
        return resp.text
    requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "walkiria", "collection": config.package, "data": resp.json()})
    config.html += f"""
        <head>
        <link rel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/styles/default.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/highlight.min.js"></script>
            <script>hljs.initHighlightingOnLoad();</script>
            <h3>ACTION URL:<br><a href="https://nuvolaris.dev/api/v1/web/gporchia/{config.package}/{name}" target="_blank">https://nuvolaris.dev/api/v1/web/gporchia/{config.package}/{name}</a></h3>
        </head>
        <body>
            <pre><code class="python"><xmp>{function}</xmp></code></pre>
        </body>
        \n\n
        """
    return f"url: https://nuvolaris.dev/api/v1/web/gporchia/{config.package}/{name}\ndescription:{description}\nfunction:{function}\n\n"

def create_action(action_array):
    config.html = ""
    actions = ""
    for x in action_array:
        description = x['description']
        name = x['name']
        function = x['function']
        actions += deploy_action(name, function, description)
    test = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/openai/tester', json={"input": actions})
    print(test.text)
    return test.text

def action_info(name):
    action_list = utils.get_actions()
    obj = json.loads(action_list)
    name_arr = []
    for x in obj:
        name_arr.append(x['name'])
    if name in name_arr:
        status = utils.action_info(config.package, name)
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
        return f"""The action url is EXACTLY this: https://nuvolaris.dev/api/v1/web/gporchia/{config.package}/{name}. ALWAYS USE THE FULL URL. Fill everythin between ``. Give information about the following action following this example:
        - **Description**: `put description here`
        - **Parameters**: `put parameters here`
        - **Code**: `put python code example that use the action`
        - **Curl**: `put curl request example to the action`
        - **Action URL**: `put the action url here`
        Format the answer as markdown
        Action:\n{status}"""
    return f""""The action you requested does not exists. Here is a list of available actions:\n{name_arr}
    """

def delete_action(name_array):
    to_obj = []
    for el in name_array:
        status = utils.delete_action(config.package, el)
        to_obj.append(json.loads(status))
    config.html = f"<html><body><pre><code><xmp>{json.dumps(to_obj, indent=2)}</xmp></code></pre></code></html>"
    return status

def show_all_actions():
    status = utils.get_actions()
    obj = json.loads(status)
    name_arr = ""
    for x in obj:
        name_arr += f"Action:{x['namespace']}/{x['name']}"
        annotations = x['annotations']
        description = ""
        for an in annotations:
            if an['key'] == 'description':
                description = an['value']
                name_arr += f"\nDescription:{description}\n"
                break
    config.html = f"<html><body><pre><code><xmp>{json.dumps(obj, indent=2)}</xmp></code></pre></code></html>"
    return f"""display ALL the following actions and the description. Example:
    - with description: **/namespace/package/action/** <br />Description: action description
    - without description: **/namespace/package/action**
    Format the answer as markdown
    Data:\n{name_arr}"""

def tools_func(
        AI: OpenAI,
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    global CLIENT
    CLIENT = AI
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
    messages.append({"role": "user", "content": "if you created and action it has been tested. Understand if you need to improve the action generated and in case you have call tools 'update_action'"})
    response = AI.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    if response.choices[0].finish_reason == "tool_calls":
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": {"output": "please wait until I finish all tests"}})
        tool_calls = response.choices[0].message.tool_calls
        return tools_func(AI, tool_calls, messages, response)
    print(response.choices[0].message.content)
    return response.choices[0].message.content

available_functions = {
    "show_all_actions": show_all_actions,
    "delete_action": delete_action,
    "action_info": action_info,
    "create_action": create_action,
    "update_action": update_action,
    "html_gen": html_gen
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
            "description": "the user asks to create an action NOT returning HTML. If the action returns html use html_gen instead",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_array": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "action name"},
                                "function": {"type": "string", "description": "the generated function. It must starts with 'def main(args):'"},
                                "description": {"type": "string", "description": "a description of the action you made. The description MUST includes the parameters the action needs such as: {key: type, key: type, ...}. Example: 'an action which add an user to the database. Required parameters: {'name': name, 'password': password, 'role': role}'"},
                                },
                                "required": ["name", "function", "description"]
                            },
                        }
                    },
                    "required": ["action_array"],
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
            "description": "the user asks informations about an action. Don't call this function if the user wants to update",
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
                            "actions_info": {
                                "type": "array",
                                "description": "Array of the actions name to be called inside the HTML. If no actions provided, return an empty array",
                                "items": {
                                    "type": "string",
                                    }
                                },
                            }
                        }
                    },
                    "required": ["args"]
                }
            }
        },
]