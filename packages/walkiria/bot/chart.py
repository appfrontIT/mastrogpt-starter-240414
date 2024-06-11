import requests
import config
import utils
from requests.auth import HTTPBasicAuth
import json
import bot_functions
from openai import OpenAI

def grapher(type = None, request = None, name = None, description = None):
    if not type or not request or not name or not description:
        return "errore: datai incompleti o errati"
    collection = type.get('collection', False)
    if collection:
        data = requests.get(f'https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/{collection}/find_many').text
    else:
        data = type.get('data', False)
    graph = requests.post(
        'https://nuvolaris.dev/api/v1/web/gporchia/grapher/create',
        json={"input": f"request:\n{request}\n\ndata:\n{data}"})
    obj = graph.json()
    editor = {"function": obj['output'], "description": description, "name": name, "namespace": config.session_user['namespace'], "package": config.session_user['username'], "language": 'html'}
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': {'editor': editor}})
    return f"Everything is fine, don't call any other function"