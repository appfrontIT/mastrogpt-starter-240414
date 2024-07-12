#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "a tester throught AI to test your actions"
#--param JWT_SECRET $JWT_SECRET
#--timeout 600000
#--annotation url https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/tester/run

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import json
import requests
import config
import re
import jwt
from requests.auth import HTTPBasicAuth

MODEL = "gpt-3.5-turbo"
AI = None
JWT = None
TOKEN = None

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
        result = r
        requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
                    auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                    json={'id': JWT['id'], 'message': {"output": json.dumps(result)}})
        ret.append(result)
    return json.dumps(ret)

def ask(query: str, AI: OpenAI, model: str = MODEL) -> str:
    messages = [
        {"role": "system", "content": config.ROLE},
        {"role": "user", "content": f"{query}\nToken for authentication: {TOKEN}"},
    ]
    for i in range(5):
        messages.append({"role": "user", "content": f"loop counter: {i + 1}"})
        response = AI.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            tools=[{
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
                                    }
                                }
                            },
                            "required": ["test_array"]
                        }
                    }
                },
            ],
            tool_choice={"type": "function", "function": {"name": "general_test"}},
        )
        if response.choices[0].message.tool_calls:
            print("loop counter " + str(i))
            messages.append(response.choices[0].message)
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                print(tool_call.function.name)
                function_name = "general_test"
                function_to_call = general_test
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
        else:
            break
    messages.append({'role': 'user', 'content': 'based on the test, provided the specifics errors and the improvement to fix them'})
    return AI.chat.completions.create(
                model=model,
                messages=messages,
            ).choices[0].message.content

def main(args):
    global AI
    global JWT
    global TOKEN
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    TOKEN = args.get('token', False)
    if not TOKEN:
        return {'statusCode': 401}
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(TOKEN, key=secret, algorithms='HS256')
    action = args.get("action", "")
    output = ask(query=action, AI=AI, model=MODEL)
    requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': JWT['id'], 'message': {"output": output}})
    return {"body": output}
