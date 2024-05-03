#--web true
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description 'an action which let you interact with a custom assistant helping you in Lookinglass operations'

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import requests
import re
import os
import veichle
import config
import ast
import pandas as pd
import tiktoken
from scipy import spatial
import bot_functions
import json
import man

MODEL = "gpt-3.5-turbo"

AI = None

messages=[{"role": "system", "content": config.LOOKINGLASS_ASSISTANT}]

EMBEDDING_MODEL = "text-embedding-3-small"

def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 100
    ) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = AI.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response.data[0].embedding
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]))
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n]

def num_tokens(text: str, model: str = MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int
) -> str:
    print("query " + query)
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query=query, df=df)
    print(strings)
    introduction = 'Use the below informations to answer the subsequent question. If the answer cannot be found in the informations, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f'\n\nLookinglass manual section:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    print(message)
    return message + question

df = pd.DataFrame

def ask(
    query: str,
    model: str = MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    # UNCOMMENT BELOW TO USE THE EMBEDDING INSTEAD OF THE MANUAL URL
    # print('ask')
    # message = query_message(query, df, model=model, token_budget=token_budget)
    # if print_message:
    #     print(message)
    # messages = [
    #     {"role": "system", "content": config.LOOKINGLASS_ASSISTANT},
    #     {"role": "user", "content": message},
    # ]
    # response = AI.chat.completions.create(
    #     model=model,
    #     messages=messages,
    # )
    # response_message = response.choices[0].message.content
    # return response_message
    messages = [{"role": "system", "content": veichle.VEICHLE_PREV_ROLE},
                {"role": "user", "content": query}]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.quotation_functions,
        tool_choice="auto"
    )
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return veichle.quotation_func(AI, tool_calls, messages, response)
    messages = [{"role": "system", "content": man.MAN_ROLE},
                {"role": "user", "content": query}]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.find_man_page,
        tool_choice="auto"
    )
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        man.find_man_func(AI, tool_calls, messages, response)
        if config.man_page != "":
            introduction = 'Use the below informations to answer the subsequent question. If the answer cannot be found in the informations, write "I could not find an answer.\n\nLookinglass manual section:\n\n"'
            question = f"\n\nQuestion: {query}"
            messages = [
                {"role": "system", "content": config.LOOKINGLASS_ASSISTANT},
                {"role": "user", "content": introduction + config.man_page + question},
                ]
            response = AI.chat.completions.create(
            model=model,
            messages=messages,
            )
            response_message = response.choices[0].message.content
            return response_message
    # """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    # message = query_message(query, df, model=model, token_budget=token_budget)
    # if print_message:
    #     print(message)
    messages = [
        {"role": "system", "content": config.LOOKINGLASS_ASSISTANT},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    response_message = response.choices[0].message.content
    return response_message

def main(args):
    global AI
    global df
    config.html = "<iframe src='https://appfront.cloud' width='100%' height='800'></iframe>"

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    cookie = args['__ow_headers'].get('cookie', False)
    if not cookie:
        return {"statusCode": 302, "headers": {"location": "https://gporchia.nuvolaris.dev"}}
    response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/user/find_by_cookie', json={"cookie": cookie})
    if response.status_code == 404:
        return {"statusCode": 404}
    config.session_user = response.json()
    
    input = args.get("input", "")
    if input == "":
        res = {
            "output": f"Bentornato {config.session_user['name']}! Come posso aiutarti?",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    else:
        output = ask(query=input, print_message=False, model=MODEL)
        res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": res})
    return { "statusCode": 204, }
