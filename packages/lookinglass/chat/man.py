from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils
from pymongo import MongoClient
import requests
from requests.auth import HTTPBasicAuth

MODEL="gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"

def find_man_page(page: str):
    query = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/embedding/retrieve', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "collection": 'crawl_appfront_operations__gitbook__io',
        'query': config.query
    })
    print(page)
    config.html = f"""
    <iframe src="https://appfront-operations.gitbook.io/lookinglass-manuale-utente/{page.lower()}" width='100%' height='800'></iframe>
    """
    return query.text