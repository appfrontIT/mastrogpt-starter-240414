#--web true
#--kind python:default
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/embedding/retrieve

from openai import OpenAI
import pandas as pd
import tiktoken
from scipy import spatial
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from bson.json_util import dumps
import os

MODEL = "gpt-4o"
AI = None
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
    token_budget: int = 4096 - 500
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses = strings_ranked_by_relatedness(query=query, df=df)
    introduction = 'Use the below informations to answer the subsequent question. If the answer cannot be found in the informations, answer to the query'
    question = f"\n\nQuestion: {query}"
    message = introduction
    for string in strings:
        next_article = f"""\n{string}\n"""
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
    return message + question


def main(args):
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    query = args.get('query', '')
    if query == '':
        return {"statusCode": 400, "body": "errore: nessuna richiesta. Passare la 'key' query con 'value' la richiesta dell'utente"}
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mcipolla']
    data = []
    collection = args.get('collection', False)
    if collection:
        coll_data = dbname[collection].find({})
        for el in coll_data:
            data.append({"text": el['text'], "embedding": el['embedding']})
    else:
        collection_list = dbname.list_collection_names()
        coll_arr = []
        for coll in collection_list:
            el = dbname[coll].find_one({})
            if el and 'embedding' in el:
                coll_arr.append(coll)
        if len(coll_arr) == 0:
            return {"statusCode": 500, "body": "nessun embedding presente all'interno del database"}
        # retrieve all collections with embedding in the schema
        for name in coll_arr:
            coll_data = dbname[name].find({})
            for el in coll_data:
                data.append({"text": el['text'], "embedding": el['embedding']})
    df = pd.DataFrame(data)
    return {"body": query_message(query=query, df=df, model='gpt-3.5-turbo')}
