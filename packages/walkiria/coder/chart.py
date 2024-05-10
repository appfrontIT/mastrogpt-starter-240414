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
    config.html = f"<iframe src='https://nuvolaris.dev/api/v1/web/gporchia/{config.session_user['package']}/{name}' width='100%' height='800'></iframe>"
    ret = {"body": graph.text}
    function = f"""def main(args):\n\treturn {ret}"""
    action = bot_functions.deploy_action(name, function, description)
    return action