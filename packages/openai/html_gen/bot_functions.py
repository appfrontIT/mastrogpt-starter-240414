from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import json
import config

MODEL="gpt-3.5-turbo"
CLIENT = None

def html_crud(args):
    description = args.get('description', '')
    model = args.get('model', '')
    print(model)
    if description == '':
        return "Error, no description provided"
    query = f"""{description}\n
    use the following example to generate the html:\n{config.html_crud}\nChange only the model informations. Model: {model}s
"""
    return query


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
    messages.append(response.choices[0].message)
    return response.choices[0].message.content

available_functions = {
    "html_crud": html_crud,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "html_crud",
            "description": "the user wants to build a CRUD application. CRUD means create, read, update, delete",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "description of the user requests"},
                            "model": {"type": "string", "description": "The Model to store in database and its attributes, formatted as: 'Model': 'attribute 1, attribute 2, attribute 3, ...'"}
                        },
                        "required": ["description", "model"]
                    },
                },
                "required": ["args"],
            },
        },
    },
]