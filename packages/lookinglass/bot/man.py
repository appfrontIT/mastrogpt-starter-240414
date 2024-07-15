from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils
from pymongo import MongoClient
import requests
from requests.auth import HTTPBasicAuth
import os

MODEL="gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"

def find_man_page(page: str):
    query = str(config.query[-1:])
    query = query.replace("[{'content': '", '')
    query = query.replace("', 'role': 'user'}]", '')
    resp = requests.post(f'https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/embedding/retrieve', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "collection": 'crawl_appfront_operations__gitbook__io',
        'query': query
    })
    config.frame = f"""https://appfront-operations.gitbook.io/lookinglass-manuale-utente/{page.lower()}"""
    return resp.text