#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which interact with a custom bot that generate actions"

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
import utils
import json
import requests

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    query: str,
    model: str = MODEL,
    print_message: bool = False,
) -> str:
    # TEST
    # from zipfile import ZipFile 
    # with ZipFile("webapp.zip", 'r') as myzip:
    #     file_list = myzip.namelist()
    #     for file in file_list:
    #         content = str(myzip.read(file))
    #         config.messages.append({"role": "user", "content": content})

    # config.messages.append({"role": "user", "content": query})
    # response = AI.chat.completions.create(
    #     model=model,
    #     messages=config.messages,
    # )
    # return response.choices[0].message.content
    # END TEST
    messages = [
        {"role": "system", "content": f"{config.EMB}"},
        {"role": "user", "content": query}
    ]
    # config.messages.append({"role": "user", "content": query})
    for i in range(5):
        print(messages)
        response = AI.chat.completions.create(
            model=model,
            messages=messages,
            tools=bot_functions.tools,
            tool_choice="auto",
        )
        # We start checking if the tools activated. If not we answer generic question about Nuvolaris
        if response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            messages = bot_functions.tools_func(AI, tool_calls, messages, response)
            messages.append({"role": "user", "content": "continue"})
        else:
            print("no tools")
            messages.append({"role": "user", "content": "Based on this conversation, provide a description of the action generated and an example using python code and curl with exact endpoint to call"})
            response = AI.chat.completions.create(model=model, messages=messages)
            return response.choices[0].message.content
    return "Couldn't find an answer"

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
                is_login = True
                stored_user = user['name']
                res = {"output": f"per favore inserire la password per l'utente {input}", "login": True}
            else:
                res = {"output": "errore, l'utente non esiste, riprovare nuovamente"}
        elif is_login == True and is_password == False:
            user = requests.get("https://nuvolaris.dev/api/v1/web/gporchia/user/find_user", headers={"Content-Type": "application/json"}, json={"name": stored_user, "password": input}).json()
            if user != None:
                is_password = True
                config.session_user = user
                res = {"output": f"Bentornato {user['name']}! Come posso aiutarti?", "password": True}
                packages = requests.get("https://nuvolaris.dev/api/v1/web/gporchia/action/get_package", json={"name": user['name']})
                obj = json.loads(packages.text)
                if obj.get('error') != None:
                    print("no package found")
                else:
                    obj = obj['actions']
                    for el in obj:
                        el.pop('version')
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
            output = ask(query=input, print_message=False, model=TUNED_MODEL)
            res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    return {"body": res,}
