#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

from openai import OpenAI
import config
import bot_functions
from secrets import token_urlsafe

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    query: list,
    model: str = MODEL,
    token_budget: int = 8192 - 500,
    print_message: bool = False,
) -> list:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    messages = [
        {"role": "system", "content": config.EMB},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=query,
        tools=bot_functions.tools,
        tool_choice="auto"
    )
    # We start checking if the tools activated. If not we answer generic question about Nuvolaris
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(AI, tool_calls, query, response)
    print("no tools")
    return "Error, something went wrong in creating your action"

TUNED_MODEL = None

cookies = {'': []}
def main(args):
    global AI
    global TUNED_MODEL
    global cookies
    config.html = config.HTML_INFO

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])
    
    TUNED_MODEL = MODEL
    headers = args['__ow_headers']
    cookie: str = headers.get("cookie", "")
    print(cookie)
    headers = ""
    input = args.get("input", "")
    if cookie == "":
        token = token_urlsafe(64)
        print(token)
        headers = {'Set-Cookie': f'UserID={token}; Max-Age=3600; Version=',}
        cookies[token] = [
            {"role": "system", "content": config.EMB},
            {"role": "user", "content": input},
            ]
        print(cookies[token])
    else:
        headers = {'Cookie': cookie}
        cookie = cookie.split('=')[1]
        cookies[cookie].append({"role": "user", "content": input})
    if input == "":
        res = {
            "output": "Benvenuti in Walkiria, la piattaforma AI di Appfront.",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    else:
        output = ask(query=cookies[cookie], print_message=False, model=TUNED_MODEL)
        cookies[cookie] = output[1]
        print(cookies[cookie])
        print(output[0])
        res = {
            "output": output[0],
        }
    if config.html != "":
        res['html'] = config.html
    return {"body": res,
            "headers": headers
            }
