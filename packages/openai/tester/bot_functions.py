import requests
import json

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
        ret += f"'expected output':'{test['output']}', 'response':'{response.text}'"
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
        ret += f"'expected output':'{test['output']}', 'response':'{response.text}'"
    return ret

def db_test(operation, test_array = []):
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
        ret += f"'expected output':'{test['output']}', 'response':'{response.text}'"
    next_op = ""
    print(operation)
    if operation == "create":
        next_op = "find"
    elif operation == "find":
        next_op = "update"
    elif operation == "update":
        next_op = "delete"
    else:
        operation = "no more operations to perform"
    return f"{ret}\n next_operation: {next_op}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "html_test",
            "description": "the API returns an html page and you have to test the inner API calls",
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
            "description": "list of tests to perform on the passed API. Take your time to perform the tests and elaborate the solution by yourself. If some tests did not pass try to run it again",
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
            "description": "you have to test operations performed to the database. You will start testing the create operation and than move to the one suggest",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "description": "the operation to perfmor on the database. The order is: create, find, update, delete"},
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
                    "required": ["operation", "test_array"]
                }
            }
        },
]