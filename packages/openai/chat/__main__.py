#--web true
#--kind python:default

from openai import AzureOpenAI
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
import bot_func
import json

MODEL = "gpt-3.5-turbo"

AI = OpenAI(api_key=api_key)
# file = AI.files.create(
#         file=open("fine_tuning.jsonl", "rb"),
#         purpose="fine-tune"
#     )
# fine_tunig = AI.fine_tuning.jobs.create(
#         training_file=file.id,
#         model=MODEL
#     )
# job_list = AI.fine_tuning.jobs.list()
# print("job list: ")
# for x in job_list:
#     print(x.id)
#     print(x.fine_tuned_model)
#     print(x.status)

messages=[{"role": "system", "content": config.LOOKINGLASS_ASSISTANT}]

bot_index = 0

BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request
embeddings = []

emb_cpy = config.EMB
EMBEDDING_MODEL = "text-embedding-3-small"

def embedding():
    batch_list = []
    for batch_start in range(0, len(emb_cpy), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = emb_cpy[batch_start:batch_end]
        batch_list.append(batch)
        response = AI.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index  # double check embeddings are in same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

    store = pd.DataFrame({"text": batch_list, "embedding": embeddings})
    # save document chunks and embeddings
    SAVE_PATH = "man.csv"
    store.to_csv(SAVE_PATH, index=False)
    df = pd.read_csv("man.csv")
    # from IPython.display import display
    # display(df)
    # convert embeddings from CSV str type back to list type
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    # the dataframe has two columns: "text" and "embedding"
    return df

df = embedding()

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
    return message + question

def exec_func(
        tool_calls: List[ChatCompletionMessageToolCall],
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    available_functions = {
        "find_link": bot_func.find_link,
        }
    messages.append(response.choices[0].message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(link=function_args.get("url"))
        messages.append({
            "tool_call_id":tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response
        })
        response = AI.chat.completions.create(model=MODEL, messages=messages)
        return response.choices[0].message.content
def ask(
    query: str,
    df: pd.DataFrame,
    model: str = MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message = query_message(query, df, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": config.LOOKINGLASS_ASSISTANT},
        {"role": "user", "content": message},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    # if response.choices[0].finish_reason == "function_call":
    #     tool_calls = response.choices[0].message.tool_calls
    #     return exec_func(tool_calls=tool_calls, messages=messages, response=response)
    response_message = response.choices[0].message.content
    bot_func.find_man(response_message, AI=AI)
    return response_message

TUNED_MODEL = None

def main(args):
    global AI
    global TUNED_MODEL
    global api_key
    global df
    config.html = "<iframe src='https://appfront.cloud' width='100%' height='800'></iframe>"

    # if fine_tunig.status == "succeeded":
    #     TUNED_MODEL = fine_tunig.fine_tuned_model
    # else:
    #     TUNED_MODEL = MODEL
    # print("model " + TUNED_MODEL)
    TUNED_MODEL = MODEL
    
    input = args.get("input", "")
    if input == "":
        res = {
            "output": "Benvenuti in Walkiria, la piattaforma AI di Appfront.",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    elif input[len(input) -1] == ' ':
        return {"body": {"output": ""}}
    else:
        output = ask(query=input, df=df, print_message=False, model=TUNED_MODEL)
        # output = ask(input)
        res = {
            "output": output
        }
    if config.html != "":
        res['html'] = config.html
    return {"body": res }
