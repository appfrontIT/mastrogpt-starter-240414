#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which interact with a custom bot that generate actions"
#--timeout 600000

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
import utils
import json
import requests
import os

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    query: str,
    model: str = MODEL,
) -> str:
    config.expand = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/prefetch/coder', json={"input": query, 'package': config.package}).text
    messages = [
        {"role": "system", "content": f"{config.EMB}"},
        {"role": "user", "content": config.expand}
    ]
    # config.messages.append({"role": "user", "content": query})
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
    )
    # We start checking if the tools activated. If not we answer generic question about Nuvolaris
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        print(response.choices[0])
        return bot_functions.tools_func(AI, tool_calls, messages, response)
    print("no tools")
    return response.choices[0].message.content

TUNED_MODEL = None
is_login = False
is_password = False
stored_user = ""

def main(args):
    global AI
    global TUNED_MODEL
    global is_login
    global is_password
    config.html = config.HTML_INFO

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    
    TUNED_MODEL = MODEL

    input = args.get("input", "")
    if input == "":
        config.messages = [{"role": "system", "content": f"{config.EMB}"}]
        is_login = False
        is_password = False
        # utils.load_zip('webapp.zip')
        res = {
            "output": "Benvenuti in Walkiria, la piattaforma AI di Appfront. Per favore, inserire il proprio nome utente",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    else:
        if is_login == False:
            user = requests.get("https://nuvolaris.dev/api/v1/web/gporchia/user/find_user", headers={"Content-Type": "application/json"}, json={"name": input}).json()
            if user != None:
                global stored_user
                stored_user = user['name']
                is_login = True
                res = {"output": f"per favore inserire la password per l'utente {input}", "login": True}
            else:
                res = {"output": "errore, l'utente non esiste, riprovare nuovamente"}
        elif is_login == True and is_password == False:
            user = requests.get("https://nuvolaris.dev/api/v1/web/gporchia/user/find_user", headers={"Content-Type": "application/json"}, json={"name": stored_user, "password": input}).json()
            if user != None:
                is_password = True
                config.session_user = user
                res = {"output": f"Bentornato {user['name']}! Come posso aiutarti?", "password": True}
                if user['role'] != 'admin':
                    packages = requests.get("https://nuvolaris.dev/api/v1/web/gporchia/package/get_package", json={"name": user['name']})
                    obj = packages.json()
                    if obj.get('error') != None:
                        obj = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/package/add_package", json={"name": user['name']}).json()
                    config.namespace = f"gporchia/{user['name']}"
                    config.package = user['name']
                    obj = obj['actions']
                else:
                    config.namespace = "gporchia"
                    config.package = 'default'
                    obj = json.loads(utils.get_actions())
                for el in obj:
                    el.pop('version')
                    # el.pop('limits')
                    # el.pop('updated')
                    annotations = []
                    for ann in el['annotations']:
                        if ann['key'] != 'raw-http' and ann['key'] != 'final' and ann['key'] != 'provide-api-key' and ann['key'] != 'exec':
                            annotations.append(ann)
                    el['annotations'] = annotations
                config.html = f"<html><body><h1>Here's a list of your actions:</h1><br><pre><code><xmp>{json.dumps(obj, indent=2)}</xmp></code></pre></code></html>"
            else:
                is_login = False
                stored_user = ""
                res = {"output": "Errore, password non valida. Per favore inserire nome utente", "password": True}
        else:
            output = ask(query=input, model=TUNED_MODEL)
            res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "db": "mastrogpt", "collection": "chat", "data": res})
    return {"body": {"status": 200}}
