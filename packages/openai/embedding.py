#--web true
#--kind python:default
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

from openai import OpenAI
import requests
import pandas as pd
import ast
import tiktoken
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from bson.json_util import dumps

MODEL = "gpt-3.5-turbo"
AI = None
BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request
embeddings = []

EMBEDDING_MODEL = "text-embedding-3-small"

def embedding(name, data):
    batch_list = []
    for batch_start in range(0, len(data), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = data[batch_start:batch_end]
        batch_list.append(batch)
        response = AI.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index  # double check embeddings are in same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

    store = pd.DataFrame({"text": batch_list, "embedding": embeddings})
    # save document chunks and embeddings
    store.to_csv('temp.csv', index=False)

    df = pd.read_csv('temp.csv')

    # convert embeddings from CSV str type back to list type
    
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
    
    # df.reset_index(inplace=True)
    data_dict = df.to_dict("records")
    # the dataframe has two columns: "text" and "embedding"
    return data_dict

def main(args):
    global AI
    name = args.get('name', '')
    if name == '':
        return {"body": "error: name is missing"}
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mastrogpt']
    collection_list = dbname.list_collection_names()
    db_coll = ""
    if name in collection_list:
        db_coll = dbname[name]
        # cursor = db_coll.find({}, {'_id': False})
        # list_cur = list(cursor)
        # json_data = dumps(list_cur)
        # return {"body": json_data}
    else:
        db_coll = dbname.create_collection(name)
    data = args.get('data', '')
    if data == '':
        return {"body": "error: data or name missing"}
    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    df = embedding(name, data)
    db_coll.insert_many(df)
    cursor = db_coll.find({}, {'_id': False})
    list_cur = list(cursor)
    json_data = dumps(list_cur)
    return {"body": json_data}
    
