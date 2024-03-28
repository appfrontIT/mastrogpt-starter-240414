#--web true
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

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

# BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request
# embeddings = []

# emb_cpy = config.EMB
# EMBEDDING_MODEL = "text-embedding-3-small"

# def embedding():
#     batch_list = []
#     for batch_start in range(0, len(emb_cpy), BATCH_SIZE):
#         batch_end = batch_start + BATCH_SIZE
#         batch = emb_cpy[batch_start:batch_end]
#         batch_list.append(batch)
#         response = AI.embeddings.create(model=EMBEDDING_MODEL, input=batch)
#         for i, be in enumerate(response.data):
#             assert i == be.index  # double check embeddings are in same order as input
#         batch_embeddings = [e.embedding for e in response.data]
#         embeddings.extend(batch_embeddings)

#     store = pd.DataFrame({"text": batch_list, "embedding": embeddings})
#     # save document chunks and embeddings
#     SAVE_PATH = "man.csv"
#     store.to_csv(SAVE_PATH, index=False)
#     df = pd.read_csv("man.csv")
#     # from IPython.display import display
#     # display(df)
#     # convert embeddings from CSV str type back to list type
#     df['embedding'] = df['embedding'].apply(ast.literal_eval)
#     # the dataframe has two columns: "text" and "embedding"
#     return df

# df = embedding()

# def strings_ranked_by_relatedness(
#     query: str,
#     df: pd.DataFrame,
#     relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
#     top_n: int = 100
#     ) -> tuple[list[str], list[float]]:
#     """Returns a list of strings and relatednesses, sorted from most related to least."""
#     query_embedding_response = AI.embeddings.create(
#         model=EMBEDDING_MODEL,
#         input=query,
#     )
#     query_embedding = query_embedding_response.data[0].embedding
#     strings_and_relatednesses = [
#         (row["text"], relatedness_fn(query_embedding, row["embedding"]))
#         for i, row in df.iterrows()
#     ]
#     strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
#     strings, relatednesses = zip(*strings_and_relatednesses)
#     return strings[:top_n], relatednesses[:top_n]

# def num_tokens(text: str, model: str = MODEL) -> int:
#     """Return the number of tokens in a string."""
#     encoding = tiktoken.encoding_for_model(model)
#     return len(encoding.encode(text))

# def query_message(
#     query: str,
#     df: pd.DataFrame,
#     model: str,
#     token_budget: int
# ) -> str:
#     print("query " + query)
#     """Return a message for GPT, with relevant source texts pulled from a dataframe."""
#     strings, relatednesses = strings_ranked_by_relatedness(query=query, df=df)
#     introduction = 'Use the below informations to answer the subsequent question. If the answer cannot be found in the informations, write "I could not find an answer."'
#     question = f"\n\nQuestion: {query}"
#     message = introduction
#     for string in strings:
#         next_article = f'\n\nLookinglass manual section:\n"""\n{string}\n"""'
#         if (
#             num_tokens(message + next_article + question, model=model)
#             > token_budget
#         ):
#             break
#         else:
#             message += next_article
#     return message + question

def ask(
    query: str,
    model: str = MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
) -> str:
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
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
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

TUNED_MODEL = None

def main(args):
    global AI
    global TUNED_MODEL
    # global df
    config.html = "<iframe src='https://appfront.cloud' width='100%' height='800'></iframe>"

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
                
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
    else:
        output = ask(query=input, print_message=False, model=TUNED_MODEL)
        res = {
            "output": output
        }
    if config.html != "":
        res['html'] = config.html
    return {"body": res }
