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

MODEL="gpt-3.5-turbo"
CLIENT = None

def create_action(name, function, description, parameters):
    print(name)
    # print(function)
    # print(description)
    # print(parameters)
    action_list = utils.get_actions()
    obj = json.loads(action_list)
    name_arr = []
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
    function = function.replace('```', '')
    function = function.replace('python', '')
    function = function.replace('Python', '')
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    body = {
        "namespace": "gporchia",
        "name": name,
        "exec":{"kind":"python:default", "code":function},
        "annotations":[
            {"key":"web-export", "value":True},
            {"key":"raw-http","value":False},
            {"key": "final", "value": True},
            {"key": "description", "value": description},
            {"key": "parameters", "value": parameters}
            ]
        }
    resp = requests.put(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}", auth=HTTPBasicAuth(split[0], split[1]), headers={"Content-type": "application/json"}, json=body)
    print(resp.text[:200])
    if resp.status_code != 200:
        return resp.text
    config.html = f"""
        <head>
        <link rel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/styles/default.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.0.3/highlight.min.js"></script>
            <script>hljs.initHighlightingOnLoad();</script>
            <h3>ACTION URL:<br><a href="https://nuvolaris.dev/api/v1/web/gporchia/default/{name}" target="_blank">https://nuvolaris.dev/api/v1/web/gporchia/default/{name}</a></h3>
        </head>
        <body>
            <pre><code class="python"><xmp>{function}</xmp></code></pre>
        </body>
        """
    html = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/openai/html_gen", json={
        "input": f"url: https://nuvolaris.dev/api/v1/web/gporchia/default/{name} action: {(resp.text)}",
        })
    print(html.text)
    config.html = f"""<iframe srcdoc="{html.json()['output']}" width="100%" height="800"></iframe>"""
    return "Action generated successfully"

def action_info(name):
    status = utils.action_info(name)
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
    return f"""The action url is: https://nuvolaris.dev/api/v1/web/gporchia/default/{name}. Fill everythin between ``. Give information about the following action following this example:
    - **Description**: `put description here`
    - **Parameters**: `put parameters here`
    - **Code**: `put python code example that use the action`
    - **Curl**: `put curl request example to the action`
    - **Action URL**: `put the action url here`
    Format the answer as markdown
    Action:\n{status}"""

def delete_action(name_array):
    to_obj = []
    for el in name_array:
        status = utils.delete_action(el)
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
    return f"""display the following actions and the description. Example:
    - with description: **/namespace/package/action/** <br />Description: action description
    - without description: **/namespace/package/action**
    Format the answer as markdown
    Data:\n{name_arr}"""

def tools_func(
        AI: OpenAI,
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list,
        response: ChatCompletion
        ):
    global CLIENT
    CLIENT = AI
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
    messages.append(response.choices[0].message)
    return [response.choices[0].message.content, messages]

available_functions = {
    "show_all_actions": show_all_actions,
    "delete_action": delete_action,
    "action_info": action_info,
    "create_action": create_action
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
            "description": "the user asks to make a function or a program",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "action name"},
                    "function": {"type": "string", "description": "the generated function. It must starts with 'def main(args):'"},
                    "description": {"type": "string", "description": "a detailed description of the function and how it works"},
                    "parameters": {
                        "type": "array",
                        "description": "an array of the function paramaters type such as '{key: type}, {key: type}, {key: type}' and so on",
                        "items": {
                            "type": "string"
                            }
                        }
                    },
                    "required": ["name", "function", "description", "parameters"],
                },
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
            "description": "the user wants to information about 1 action",
            "parameters": {
                "type": "object",
                "properties": {
                    "name" : {"type": "string", "description": "the name of the action, it must be 1 word"}
                },
                    "required": ["name"],
                },
            }
        },
]