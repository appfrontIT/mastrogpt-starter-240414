#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which interact with a custom bot to invoke administration tasks"

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
import json
import requests

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    query: str,
    model: str = MODEL,
) -> str:
    config.messages.append({"role": "user", "content": query})
    response = AI.chat.completions.create(
        model=model,
        messages=config.messages,
        tools=bot_functions.tools,
        tool_choice="auto",
        max_tokens=(4096 - 500)
    )
    # We start checking if the tools activated. If not we answer generic question about Nuvolaris
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(AI, tool_calls, config.messages, response)
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

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    
    TUNED_MODEL = MODEL

    input = args.get("input", "")
    if input == "":
        config.messages = [{"role": "system", "content": f"{config.EMB}"}]
        is_login = False
        is_password = False
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
                if user['role'] != 'admin':
                    res = {"output": "errore: devi essere un admin per utilizzare questa sezione"}
                else:
                    res = {"output": f"Bentornato {user['name']}! Come posso aiutarti?", "password": True}
                    config.namespace = "gporchia"
                    config.package = 'default'
                    users = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "users", "data": {"filter": {}}})
                    config.html = f"<html><body><h1>In this section you can create, update, and delete an user!</h1><br><h2>Current users:</h2><br><pre><code><xmp>{json.dumps(users.json(), indent=2)}</xmp></code></pre></code></html>"
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
    return {"body": res,}
