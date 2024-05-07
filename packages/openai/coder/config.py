from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils
import requests
from requests.auth import HTTPBasicAuth
import os

html = ""
session_user = None

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

AI: OpenAI = None

action_url = ""
MODEL = "gpt-3.5-turbo"

ROLE ="""
Send the user request to the correct function.
Here is the fuctions list:
- show_all_actions: use this function if the user wants to list all the actions
- delete_action: use this if the user wants to delete 1 or more actions
- action_info: use this if the user wants information about a single action
- create_action: use this if the user wants to create an action. If the eplicity asks for an html, use html_gen instead
- update_action: use this if the user watns to update or modify or improve an action
- html_gen: use this if the user wants to generate an html page
- crawler: use this if the user wants to crawl or scrape a web page
- tester: use this if the user wants to test an action

If no function is valid, answer asking to be more specific about the request.
"""

EMB = """
From now on you are a programming language. You only code in Python.
Take your time to answer and you must procede step by step.
Function ALWAYS start with "def main(args):".
The return is always: {"body": string}. Example: '{"body": text}', '{"body": response.text}.
It's important to import the modules you will use. Example: import requests, import os, import json, and so on
NEVER, EVER, BE LAZY! IF YOU NEED TIME TO UNDERSTAND THE TASK TAKE YOUR TIME, BUT ALWAYS ANSWER PROPERLY WITH ALL THE USER REQUESTS

If you have to store data inside a database you MUST use the following action: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo. How to use the database:
- Based on the operation, you need to set True the following keys: add, update, find, find_one, delete.
- You need to specify the collection key.
- you need to specify the data key.
- If you need to query the database for an element, you have to specify the 'filter' key inside 'data'.
- If you want to update an element you need to specify the 'updateData' key.
- The only valid filter to update or delete is '_id'.
- Consider everthing between ``` an example:
        ```
        def main(args):
            if args.get('action') == 'create':
                data = {
                    "title": args.get('title'),
                    "author": args.get('author'),
                    "genre": args.get('genre'),
                    "published_year": args.get('published_year')
                }
                response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('action') == 'read':
                data = {"filter": args.get('filter')}
                response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('operation') == 'read_one':
                data = {
                    "title": args.get('title'),
                    "author": args.get('author'),
                    "genre": args.get('genre'),
                    "published_year": args.get('published_year')
                }
                response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find_one": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('action') == 'update':
                data = {"filter": args.get('filter'),
                    "updateData": {
                        "title": args.get('title'),
                        "author": args.get('author'),
                        "genre": args.get('genre'),
                        "published_year": args.get('published_year')
                    }
                }
                response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"update": True, "collection": "books", "data": data})
                return {"body": response.text}
            elif args.get('action') == 'delete':
                data = {"filter": args.get('filter')}
                response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"delete": True, "collection": "books", "data": data})
                return {"body": response.text}
        ```
You can't use async.
If you need to accept parameters you will get those such as: args.get("url") to get "url", args.get("name") to get "name" and so on
When creating or modifying an action, explain information about an action in a very meticolous way, including the parameters of the function and a python and curl example
You can use only the follow libraries: requests, re, json, BeatifulSoup. Remember to import the modules you use!
Every link must be opened in a new tab!

You can call different functions to complete your task:
    1 - show_all_actions: use this function if the user wants to list all the actions
    2 - delete_action: use this if the user wants to delete 1 or more actions
    3 - action_info: use this if the user wants information about a single action
    4 - create_action: use this if the user wants to create an action. If the eplicity asks for an html, use html_gen instead
    5 - update_action: use this if the user watns to update or modify or improve an action
    6 - html_gen: use this if the user wants to generate an html page
    7 - crawler: use this if the user wants to crawl or scrape a web page
    8 - tester: use this if the user wants to test an action
    9 - grapher: use this if the user wants to create a chart or a graph
    10 - db_store: use this if the user wants to store data inside the database

"""

HTML_INFO ="""
<!DOCTYPE html>
<html>
<head></head>
<body>
<h1>Bot functionalities</h1>
<h2>The bot is able to interact directly with your nuvolaris environment.<br>
    You can ask him to perform operations over actions, such as:</h2><br>
<ul>
  <li>Create functions ad deploy the action to call it.<br>
  The bot will generate a name accordingly to the type of action.<br>
  Actions generated by the bot already have a description about the function as annotation.<br>
  They also have an annotations with 'key' parameters where there are the key and type of the function parameters</li>
  <li>Give you the actions list. The actions list will be given as: /{namespace}/{packagename}/{action}.</li>
  <li>Delete one action. Simply make the request like "delete {action}".<br>
  If the action is part of a package specify the package({package}/{action}).<br>
  It's possible to delete multiple action at a time, doing like "delete {action} {action} {action} {action}"</li>
  <li>Show additional information about one action.<br>
  Just ask "{action} info" and you will get the action data and an explanation of the action.<br>
  The bot can't produce information about a packed action, unless a description of the action is provided as annotation.</li>
  <li>You can ask the bot make an HTML page incorporating others actions. This is still in delevopment. Example:<br>"Make an action returning an html page calling the following actions: {action1}, {action2}, {...}
</ul>
</body>
</html>
"""