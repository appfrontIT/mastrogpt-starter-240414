from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import requests
import requests
import json
import config

MODEL="gpt-3.5-turbo"
CLIENT = None

def create_user(name, password, role = 'user'):
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/user/add",
                            json={"name": name, "password": password, "role": role})
    users = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "users", "data": {"filter": {}}})
    config.html = f"<html><body><h1>In this section you can create, update, and delete an user!</h1><br><h2>Current users:</h2><br><pre><code><xmp>{json.dumps(users.json(), indent=2)}</xmp></code></pre></code></html>"
    return response.text

def update_user(name, role = 'user'):
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/user/update",
                            json={"name": name, "role": role})
    users = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "users", "data": {"filter": {}}})
    config.html = f"<html><body><h1>In this section you can create, update, and delete an user!</h1><br><h2>Current users:</h2><br><pre><code><xmp>{json.dumps(users.json(), indent=2)}</xmp></code></pre></code></html>"
    return response.text

def delete_user(id):
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/user/del",
                            json={"_id": id})
    users = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "users", "data": {"filter": {}}})
    config.html = f"<html><body><h1>In this section you can create, update, and delete an user!</h1><br><h2>Current users:</h2><br><pre><code><xmp>{json.dumps(users.json(), indent=2)}</xmp></code></pre></code></html>"
    return response.text

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
    response = AI.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

available_functions = {
    "create_user": create_user,
    "update_user": update_user,
    "delete_user": delete_user
}

tools = [
        {
        "type": "function",
        "function": {
            "name": "show_all_users",
            "description": "the administrator want to display or list all the users",
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
            "name": "create_user",
            "description": "the administrator asks to create a new user. It must be specify the name, password and role",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "name of the user to be generated"},
                    "password": {"type": "string", "description": "password of the user to be generated"},
                    "role": {"type": "string", "description": "role of the user to be generated"}
                    },
                    "required": ["name", "password", "role"],
                },
            },
        },
        {
        "type": "function",
        "function": {
            "name": "update_user",
            "description": "modify an user. Example: update 'user' role to 'new role'",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "user name"},
                    "role": {"type": "string", "description": "the user new role"},
                    },
                    "required": ["name", "role"],
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "delete_user",
            "description": "delete an user by id. Example: delete 'user id'",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "the id of the user to delete"},
                    },
                    "required": ["id"],
                }
            }
        },
]