#--web true
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "a tester throught AI to test your actions"

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import json
import requests
import config
import bot_functions

AI = None
MODEL = "gpt-3.5-turbo"

available_functions = {
    "html_test": bot_functions.html_test,
    "general_test": bot_functions.general_test
}

def ask(query: str, model: str = MODEL) -> str:
    messages = [
        {"role": "system", "content": config.ROLE},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
    )
    if response.choices[0].finish_reason != "tool_calls":
        return response.choices[0].message.content
    messages.append(response.choices[0].message)
    tool_calls = response.choices[0].message.tool_calls
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
    messages.append({"role": "user", "content": "check if in the passed data there are failed tests and report them. Suggest some improvements if needed. Taske your time to answer"})
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content
TUNED_MODEL = None

def main(args):
    global AI
    global TUNED_MODEL
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    
    TUNED_MODEL = MODEL

    input = args.get("input", "")
    output = ask(query=input, model=TUNED_MODEL)
    return {"body": {"output": output}}