#--web false
#--kind python:default
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/embedding/embed

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
    collection = args.get('collection', None)
    token = args.get('token', None)
    if collection == None:
        return { "statusCode": 404, "body": "error: collection is missing"}
    if token == None:
        return {'statusCode': 401}
    connection_string = args.get('CONNECTION_STRING', False)
    client = MongoClient(connection_string)
    dbname = client['mastrogpt']
    collection_list = dbname.list_collection_names()
    if collection not in collection_list:
        return {'statusCode': 400, 'body': 'collection not found'}
    db_coll = dbname[collection]
    el = db_coll.find_one()
    if 'text' not in el:
        return {'statusCode': 400, 'body': 'Collection must have key text for embedding'}
    cursor = db_coll.find()
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    for document in cursor:
        embedded_response = AI.embeddings.create(model="text-embedding-3-small", input=document['text'])
        embedded_data = embedded_response.data[0].embedding
        db_coll.update_one({'_id': document['_id']}, {"$set": {"embedding": embedded_data}})
    return {"statusCode": 204}
    