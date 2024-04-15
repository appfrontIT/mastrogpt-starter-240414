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

def tools_func(
        AI: OpenAI,
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    global CLIENT
    CLIENT = AI
    temp = messages.copy()
    temp.append(response.choices[0].message)
    for tool_call in tool_calls:
        print(tool_call.function.name)
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(
            **function_args
            )
        temp.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response
        })
    response = AI.chat.completions.create(model=MODEL, messages=temp)
    config.messages.append(response.choices[0].message)
    return response.choices[0].message.content

available_functions = {
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
                    "modifications": {"type": "string", "description": "the admin requested modifications"},
                    },
                    "required": ["name", "modifications"],
                }
            }
        },
]