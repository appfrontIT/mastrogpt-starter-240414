from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils

MAN_ROLE="""
Find the correct Manual page reference the user is asking for between:
Accesso
Main
Articoli
Dashboard
Intermediari
Utenti
Profili
Utenza
Preventivi
Polizze
Titoli
Post vendita
"""
MODEL="gpt-3.5-turbo"

def find_man_page(page: str):
    man_page = utils.crawl(f"https://appfront-operations.gitbook.io/lookinglass-manuale-utente/{page.lower()}")
    config.html = f"""
    <iframe src="https://appfront-operations.gitbook.io/lookinglass-manuale-utente/{page.lower()}" width='100%' height='800'></iframe>
    """
    if man_page != "":
        config.man_page = man_page
    return "ok"

def find_man_func(
        AI: OpenAI,
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
) -> str:
    available_functions = {
        "find_man_page": find_man_page,
        }
    messages.append(response.choices[0].message)
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
    response = AI.chat.completions.create(model=MODEL, messages=messages)