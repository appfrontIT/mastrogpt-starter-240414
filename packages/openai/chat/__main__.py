#--web true
#--kind python:default
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param OPENAI_API_HOST $OPENAI_API_HOST

from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
import requests
import re
import os
import veichle
import config
import ast
import pandas as pd
import tiktoken
from scipy import spatial
import utility

LOOKINGLASS_ASSISTANT="""
You are a Lookinglass assistan for company employers.
You only answer ensurance, financial questions, quotations.
Always answer in the user language.
Never suggest to call any company outside Lookinglass. Avoid suggesting an expert.
If you can't answer, just answer "Sorry, I can't answer this question".
"""

EMBEDDING_MODEL = "text-embedding-ada-002"
MODEL = "gpt-35-turbo"
AI = None

messages=[{"role": "system", "content": LOOKINGLASS_ASSISTANT}]

bot_index = 0

BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request
embeddings = []
# df = pd.DataFrame()
def embedding():
    for batch_start in range(0, len(config.EMB), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = config.EMB[batch_start:batch_end]
        response = AI.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index  # double check embeddings are in same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

    store = pd.DataFrame({"text": config.EMB, "embedding": embeddings})

    # save document chunks and embeddings
    SAVE_PATH = "man.csv"
    store.to_csv(SAVE_PATH, index=False)
    df = pd.read_csv("man.csv")
    # convert embeddings from CSV str type back to list type
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    # the dataframe has two columns: "text" and "embedding"
    return df

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
        {"role": "system", "content": LOOKINGLASS_ASSISTANT},
        {"role": "user", "content": message},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message

# def ask(input):
#     # if not config.is_veichle_pr and not config.is_man:
#     #     find_context(input)
#     query = f"""
#     Use the following information to answer the subsequent question. if the answer cannot be found, write "I don't know".

#     information:
#     {config.EMB}

#     Question: {input}
#     """
#     input_mex = {"role": "user", "content": query}
#     if config.is_man:
#         comp: ChatCompletion = veichle.is_man(AI, input_mex)
#     elif config.is_veichle_pr:
#         comp: ChatCompletion = veichle.is_veichle(AI, input_mex)
#     else:
#         messages.append(input_mex)
#         comp = AI.chat.completions.create(model=MODEL, messages=messages)
#         messages.append({"role": "assistant", "content": comp.choices[0].message.content})
#     if len(comp.choices) > 0:
#         content = comp.choices[0].message.content
#         return content
#     return "ERROR"

def main(args):
    global AI
    config.html = ""
    (key, host) = (args["OPENAI_API_KEY"], args["OPENAI_API_HOST"])
    AI = AzureOpenAI(api_version="2023-12-01-preview", api_key=key, azure_endpoint=host)
    
    df = embedding()

    input = args.get("input", "")
    if input == "":
        res = {
            "output": "Welcome to Lookinglass, how can I help you today? You can make a quotation or ask help in execute a task",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    else:
        print(input)
        output = ask(query=input, df=df)
        res = {
            "output": output
        }
    if config.html != "":
        res['html'] = config.html
    return {"body": res }
