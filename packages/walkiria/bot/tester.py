import requests
import config
import utils
from requests.auth import HTTPBasicAuth
import json

def tester(name = None):
    if not name:
        return "errore: devi specificare il nome dell'azione da testare"
    action = utils.action_info(config.session_user['package'], name)
    action_obj = json.loads(action)
    error = action_obj.get('error', '')
    if error != '':
        return f"the following action does not exists: {name}\n"
    action_s = f"name: {action_obj['name']}\n"
    annotations = action_obj['annotations']
    for pair in annotations:
        if pair['key'] == 'url' or pair['key'] == 'description':
            action_s += f"{pair['key']}: {pair['value']}\n"
    action_s += f"code: {action_obj['exec']['code']}\n"
    test = requests.post(
        'https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/tester/run',
        auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
        json={"action": action_s, "token": config.session_user['JWT']})
    return test.text