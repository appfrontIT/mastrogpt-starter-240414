import requests
import config
import utils
from requests.auth import HTTPBasicAuth
import json
import bot_functions
from openai import OpenAI
import config
import os

def grapher(type = None, request = None, name = None, description = None):
    if not type or not request or not name or not description:
        return "errore: datai incompleti o errati"
    collection = type.get('collection', False)
    if collection:
        data = requests.get(f'https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/db/mongo/{collection}/find_many',
                            headers={'Authorization': 'Bearer ' + config.session_user[ 'JWT']}).json()
    else:
        data = type.get('data', False)
    graph = requests.post(
        f'https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/grapher/create?blocking=true',
        auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
        json={"input": f"request:\n{request}\n\ndata:\n{data}"})
    obj = graph.json()
    editor = {"function": obj['output'], "description": '', "name": name, "namespace": '', "package": '', "language": 'html'}
    requests.post(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': {'editor': editor}})
    return f"Everything is fine, don't call any other function"