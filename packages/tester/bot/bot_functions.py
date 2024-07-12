from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
from bs4 import BeautifulSoup
import requests
import os
from requests.auth import HTTPBasicAuth
import json
import config

MODEL="gpt-3.5-turbo"

def general_test(test_array = []):
    if len(test_array) == 0:
        return "couldn't generate any test for the passed API"
    ret = []
    for test in test_array:
        print(test)
        response = ""
        url = test.get('url')
        headers = json.loads(test.get('headers', '{}').replace("'", '"'))
        body = json.loads(test.get('body', '{}').replace("'", '"'))
        if test.get('method') == 'GET':
            try:
                response = requests.get(url)
                r = {"test": test, 'response': {"status": response.status_code, "body": response.text}}
            except requests.exceptions.RequestException as e:
                r = e
        elif test.get('method') == 'POST':
            try:
                response = requests.post(url, headers=headers, json=body)
                r = {"test": test, 'response': {"status": response.status_code, "body": response.text}}
            except requests.exceptions.RequestException as e:
                r = e
        elif test.get('method') == 'PUT':
            try:
                response = requests.put(url, headers=headers, json=body)
                r = {"test": test, 'response': {"status": response.status_code, "body": response.text}}
            except requests.exceptions.RequestException as e:
                r = e
        elif test.get('method') == 'DELETE':
            try:
                response = requests.delete(url, headers=headers, json=body)
                r = {"test": test, 'response': {"status": response.status_code, "body": response.text}}
            except requests.exceptions.RequestException as e:
                r = e
        elif test.get('method') == 'HEAD':
            try:
                response = requests.get(url)
                r = {"test": test, 'response': {"status": response.status_code, "body": response.text}}
            except requests.exceptions.RequestException as e:
                r = e
        result = r
        requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
                    auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                    json={'id': config.session_user['_id'], 'message': {"output": json.dumps(result)}, 'history': {"role": "assistant", "content": json.dumps(result)}})
        ret.append(result)
    return json.dumps(ret)

tools = [
        {
        "type": "function",
        "function": {
            "name": "general_test",
            "description": "list of tests to perform on the passed API. Take your time to perform the tests and elaborate the solution by yourself before. Ensure tests are valid JSON",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_array": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string", "description": "method to use with the API. Can be: 'GET', 'POST', 'PUT', 'DELETE', 'HEAD'"},
                                "url": {"type": "string", "description": "endpoint to call"},
                                "body": {"type": "string", "description": """body to pass to the API if needed. Always read API description to understand the keys name. Example: "body": "{'arg1': string}" """},
                                "headers": {"type": "string", "description": """headers to pass to the API. Must be a python dictionary. Example: "headers": "{'Content-Type': 'application/json'}" """},
                                "output": {"type": "string", "description": "expected output by the API call"}
                                },
                                "required": ["method", "url", "headers", "output"]
                            },
                        },
                    },
                    "required": ["test_array"]
                }
            },
        },
]
