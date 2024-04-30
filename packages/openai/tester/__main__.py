#--web true
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "a tester throught AI to test your actions"
#--timeout 600000

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import json
import requests
import config

MODEL = "gpt-3.5-turbo"
AI = None

def general_test(test_array = []):
    if len(test_array) == 0:
        return "couldn't generate any test for the passed API"
    ret = ""
    for test in test_array:
        print(test)
        response = ""
        if test.get('method') == 'GET':
            response = requests.get(test.get('url'))
        elif test.get('method') == 'POST':
            response = requests.post(test.get('url'), headers=json.loads(test.get('headers')), json=json.loads(test.get('body')))
        elif test.get('method') == 'PUT':
            response = requests.put(test.get('url'),headers=json.loads(test.get('headers')), json=json.loads(test.get('body')))
        elif test.get('method') == 'DELETE':
            response = requests.delete(test.get('url'),headers=json.loads(test.get('headers')), json=json.loads(test.get('body')))
        elif test.get('method') == 'HEAD':
            response = requests.head(test.get('url'))
        result = f"test:'{test}', 'response':'{response.text}'"
        print(result)
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": {"output": result}})
        ret += result
    return ret

def ask(query: str, AI: OpenAI, model: str = MODEL) -> str:
    messages = [
        {"role": "system", "content": config.ROLE},
        {"role": "user", "content": query},
    ]
    for i in range(5):
        messages.append({"role": "user", "content": f"loop counter: {i + 1}"})
        response = AI.chat.completions.create(
            model=model,
            messages=messages,
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
                                        "body": {"type": "string", "description": """body to pass to the API if needed. Always read API description to understand the keys name. Example: "body": {"arg1": string}"""},
                                        "headers": {"type": "string", "description": """headers to pass to the API. Must be a python dictionary. Example: "headers": {"Content-Type": "application/json"}"""},
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
    return AI.chat.completions.create(
                model=model,
                messages=messages,
            ).choices[0].message.content

def main(args):
    global AI
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    input = args.get("input", "")
    output = ask(query=input, AI=AI, model=MODEL)
    return {"body": {"output": output}}
