from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import json
import config
import requests

MODEL="gpt-4o"
CLIENT = None

def html_crud(args):
    description = args.get('description', '')
    model = args.get('model', '')
    if description == '':
        return "Error, no description provided"
    query = f"""{description}\n
    use the following example to generate the html:\n{config.html_crud}\nChange only the model informations. Model: {model}
"""
    return query

def html_general(description, actions = []):
    return f"""Generate an HTML page representing the following description: {description}
    the html page should call the following actions if provided: {actions}
    Take your time to generate the html. If you need to perform any http request use javascript.
    try to format the page in a well and aesthetical way. Use a css style to make everything look better.
    Use cols and rows if needed to format the page better."""

def single_page_scrape(url = None):
    if url == None:
        return "no url provided"
    response = requests.post(url)
    print(response.text)
    return response.text

def create_grid(html = None):
    if not html:
        return "there was an error generating html"
    return html

def add_js(html = None):
    if not html:
        return "there was an error generating html"
    return html

def add_css(html = None):
    if not html:
        return "there was an error generating html"
    return html

def tools_func(
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    # requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], "message": {"output": "Certo, procedo subito con la tua richiesta"}})
    while True:
        tool_calls = response.choices[0].message.tool_calls
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
            print(function_response)
        response = config.AI.chat.completions.create(model='gpt-4o', messages=messages, tools=tools, tool_choice="auto", temperature=0.1, top_p=0.1)
        if response.choices[0].finish_reason != "tool_calls":
            break
        # requests.post("https://walkiria.cloud/api/v1/namespaces/mcipolla/actions/db/load_message",
        #             auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
        #             json={'id': config.session_user['_id'], "message": {"output": "Sto elaborando la tua richiesta, per favore attendi"}}
        #             )
    return response.choices[0].message.content

available_functions = {
    "html_crud": html_crud,
    "html_general": html_general,
    "single_page_scrape": single_page_scrape,
    "create_grid": create_grid,
    "add_js": add_js,
    "add_css": add_css,
}

tools = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "html_crud",
    #         "description": "the user wants to build a CRUD application. CRUD means create, read, update, delete",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "args": {
    #                     "type": "object",
    #                     "properties": {
    #                         "description": {"type": "string", "description": "description of the user requests"},
    #                         "model": {"type": "string", "description": "The Model to store in database and its attributes, formatted as: 'Model': 'attribute 1, attribute 2, attribute 3, ...'"}
    #                     },
    #                     "required": ["description", "model"]
    #                 },
    #             },
    #             "required": ["args"],
    #         },
    #     },
    # },
    {
            "type": "function",
            "function": {
                "name": "single_page_scrape",
                "description": """scrape a single page skipping all sublinks and extract text. Use this if you the user ask for informations or summary about a page.
                You can also use this function for yourself, by asking the user a webpage where you can gather informations to answer the question""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "the url to scrape"}
                    },
                    "required": ["url"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_grid",
                "description": "create the skeleton of the html page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "html": {"type": "string", "description": "the html page skeleton structure"}
                    },
                    "required": ["html"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_js",
                "description": "add javascript to the page skeleton",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "html": {"type": "string", "description": "the html page skeleton plus the javascript"}
                    },
                    "required": ["html"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_css",
                "description": "add css to the skeleton + javascript page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "html": {"type": "string", "description": "the html page skeleton plus the javascript plus the css"}
                    },
                    "required": ["html"],
                }
            }
        }
]