#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which interact with a general purpose chat bot"
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/base/bot

from openai import OpenAI
import json
import requests
from requests.auth import HTTPBasicAuth
import os

MODEL = "gpt-4o"
OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
QUERY: str = ""
AI: OpenAI = None

def ask(
    messages,
    input,
    model: str = MODEL,
) -> str:
    global AI
    query = str(input[-1:])
    query = query.replace("[{'content': '", '')
    query = query.replace("', 'role': 'user'}]", '')
    resp = requests.post(f'https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/embedding/retrieve', json={
        "collection": 'crawl_appfront__cloud',
        'query': query
    })
    messages.extend([{'role': 'user', 'content': resp.text}])
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content

def main(args):
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    session_user = args.get('user', False)
    if not session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    input = args.get("input", "")
    if input == "":
        return { "statusCode": 204, }  
    else:
        messages = [{'role': 'system', 'content': ROLE}]
        res = { "output": ask(messages=messages, input=input, model=MODEL)}
    requests.post(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': session_user['_id'], 'message': res})
    return {"statusCode": 200, 'body': res['output']}

ROLE = """
You're an Appfront assistant. You answer general question about Appfront.
The user interface with you through a web page. In this page the user can choose between differents chatbot, each one with a specific scope:
    - Lookinglass: this bot answer general question about Lookinglass ensurance company, especially over the manual. It can also generate quotations.
    - Coder: this bot is used to generate actions. Actions are stateless functions that run on a serverless platform.
    - Admin: this bot is used to administration purpose, like manage the actions, users or packages.
    - Website: this bot will help the user generating a web page. Usually web page are built to work as interface to the actions.
    - Chart: this bot will help the user generating charts. The charts are build using chartjs, and providing the data to use in the chart.
    Most of the bot come with an interface, to be used to simplify the query to send to the corresponding bot.
In the page, the user could also find different sections:
    - scraped: this section display the domains scraped by the coder bot.
    - swagger: this section display all the openAPI spec to interact with Appfront API.
    - a button with whom you can access personal sections, which are:
        - logout: used to logout the user.
        - my swagger: used to display the openAPI spec of the actions created by the user. The specs are automatically created by the bot each time an action is created.
        - my pages: used to display all the web pages generated by the bot.
        - my files: used to display all the file uploaded by the user.
        - settings: used to set user parameters
"""