import requests
import json
import config

def html_test(test_array = []):
    if len(test_array) == 0:
        return "couldn't generate any test for the passed API"
    ret = ""
    for test in test_array:
        response = ""
        print(test)
        if test['method'] == 'GET':
            response = requests.get(test['url'])
        elif test['method'] == 'POST':
            response = requests.post(test['url'],headers=json.loads(test['headers']), json=json.loads(test['body'].replace("'", '"')))
        elif test['method'] == 'PUT':
            response = requests.put(test['url'],headers=json.loads(test['headers']), json=json.loads(test['body'].replace("'", '"')))
        elif test['method'] == 'DELETE':
            response = requests.delete(test['url'],headers=json.loads(test['headers']), json=json.loads(test['body'].replace("'", '"')))
        elif test['method'] == 'HEAD':
            response = requests.head(test['url'])
        result = f"'expected output':'{test['output']}', 'response':'{response.text}'"
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": {"output": f"test:\n{test}\nresult:\n{result}"}})
        ret += result
    return ret

def general_test(test_array = []):
    if len(test_array) == 0:
        return "couldn't generate any test for the passed API"
    ret = ""
    for test in test_array:
        print(test)
        response = ""
        if test['method'] == 'GET':
            response = requests.get(test['url'])
        elif test['method'] == 'POST':
            response = requests.post(test['url'], headers=json.loads(test['headers']), json=json.loads(test['body'].replace("'", '"')))
        elif test['method'] == 'PUT':
            response = requests.put(test['url'],headers=json.loads(test['headers']), json=json.loads(test['body'].replace("'", '"')))
        elif test['method'] == 'DELETE':
            response = requests.delete(test['url'],headers=json.loads(test['headers']), json=json.loads(test['body'].replace("'", '"')))
        elif test['method'] == 'HEAD':
            response = requests.head(test['url'])
        result = f"'expected output':'{test['output']}', 'response':'{response.text}'"
        requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": {"output": f"test:\n{test}\nresult:\n{result}"}})
        ret += result
    return ret

def db_test(actions_array = []):
    if len(actions_array) == 0:
        return "couldn't generate any test for the passed API"
    ret = ""
    messages = [
        {"role": "system", "content": config.ROLE},
        {"role": "system", "content": "I will send a list of action permorming operations to a database. Collect the answer and use it to construct the next tests"}
    ]
    for action in actions_array:
        print(action)
        messages.append({"role": "user", "content": str(action)},)
        response = config.AI.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "general_test"}},
        )
        if response.choices[0].finish_reason == "tool_calls":
            messages.append(response.choices[0].message)
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                print(tool_call.function.name)
                function_name = tool_call.function.name
                function_to_call = general_test
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    **function_args
                    )
                ret += function_response
                messages.append({
                    "tool_call_id":tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })

    return ret

tools = [
    {
        "type": "function",
        "function": {
            "name": "html_test",
            "description": "the API returns an html page and you have to test the inner fetches. Take your time, read the action and extract the information inside the '<script>' inside the html",
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
                                "body": {"type": "string", "description": "body associated with the API call inside the html"},
                                "headers": {"type": "string", "description": "headers associated with the API call inside the html"},
                                "output": {"type": "string", "description": "expected output by the API call"}
                                },
                                "required": ["method", "url", "output"]
                            }
                        }
                    },
                    "required": ["test_array"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "general_test",
            "description": "list of tests to perform on the passed API. Take your time to perform the tests and elaborate the solution by yourself. Don't call this function for actions that use database",
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
        {
        "type": "function",
        "function": {
            "name": "db_test",
            "description": "an array of the action to test that call the database. The order should be: create, find, update, delete",
            "parameters": {
                "type": "object",
                "properties": {
                    "actions_array": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "name of the action"},
                                "description": {"type": "string", "description": "complete description of the action with parameters"},
                                "function": {"type": "string", "description": """fucntion to test"""},
                                },
                                "required": ["name", "description", "function"]
                            },
                        },
                    },
                },
                "required": ["actions_array"]
            },
        },
]