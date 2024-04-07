#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--param LOGIN $LOGIN
#--param PASSWORD $PASSWORD

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe
import utils
import json

AI = None
MODEL = "gpt-3.5-turbo"

action_list = utils.get_actions()
obj = json.loads(action_list)
action_info_training = ""
for x in obj:
    namespace = x['namespace']
    if namespace == "gporchia/openai" or namespace == "gporchia/mastrogpt" or namespace == "gporchia/db":
        continue
    split = namespace.split('/')
    if len(split) > 1:
        _name = f"{split[1]}/{x['name']}"
        data = utils.action_info(_name)
        obj = json.loads(data)
        action_info_training += f"{utils.action_info(_name)}\n"
    else:
        data = utils.action_info(x['name'])
        obj = json.loads(data)
        action = f"name={obj['name']}\nurl={obj['annotations'][1]['value']}\ndescription={obj['annotations'][2]['value']}\nparameters={obj['annotations'][7]['value']}"
        action_info_training += f"{action}\n"


config.messages = [{"role": "system", "content": f"{config.EMB}"}, {"role": "user", "content": f"Complete list of the actions:\n{action_info_training}"}]

def ask(
    query: str,
    model: str = MODEL,
    print_message: bool = False,
) -> str:
    # find_actions = AI.chat.completions.create(
    #     model=model,
    #     messages=[
    #         {"role": "system", "content": """Return an array of action names user is asking to use. Example: {"actions": []}"""},
    #         {"role": "user", "content": query}
    #     ]
    # ).choices[0].message.content
    # obj = json.loads(str(find_actions))
    # array = obj.get('actions', '')
    # print(array)
    # if len(array) > 0:
    #     query_actions = ""
    #     for x in array:
    #         data = utils.action_info(x)
    #         obj = json.loads(data)
    #         if len(obj.get('error')) > 0:
    #             return f"the following action does not exists: {x}\n"
    #         action = f"name={obj['name']}\nurl={obj['annotations'][1]['value']}\ndescription={obj['annotations'][2]['value']}\nparameters={obj['annotations'][7]['value']}"
    #         query_actions += f"{action}\n"
    #     query = f"use the following informations to answer:\n{query_actions}Question:{query}"
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
    print("no tools")
    return response.choices[0].message.content

TUNED_MODEL = None
is_login = False
is_password = False

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
        res = {
            "output": "Benvenuti in Walkiria, la piattaforma AI di Appfront. Per favore, inserire il proprio nome utente",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    else:
        if is_login == False:
            if input == args.get("LOGIN"):
                is_login = True
                res = {"output": f"per favore inserire la password per l'utente {input}"}
            else:
                res = {"output": "errore, l'utente non esiste, riprovare nuovamente"}
        elif is_login == True and is_password == False:
            if input == args.get("PASSWORD"):
                is_password = True
                user = args.get("LOGIN")
                res = {"output": f"Bentornato {user}! Come posso aiutarti?"}
            else:
                is_login = False
                res = {"output": "Errore, password non valida. Per favore inserire nome utente"}
        else:
            output = ask(query=input, print_message=False, model=TUNED_MODEL)
            res = { "output": output}
    if config.html != "":
        res['html'] = config.html
    return {"body": res,}
