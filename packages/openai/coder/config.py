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

ROLE = """
You're a Personal assistant. Most of the time you should call internal functions to accomplish the task.
You must analyze the user request and understand if and which function to call.
Be talkative, you should act like a Human. Sometimes it will be hard to understand the user request, but you can ask to calirifications any time.
Open links in an external tab, always!

If you're not totally sure which function to call, you can ask the user to clear your doubts. Example:
{
    "user": "how do you use get_next_line action?"
    "assistant": "are you looking for some information and use cases about get_next_line?"
    "user": "yes exactly!"
    "assistant": "<call internal function action_info>"
}

Take your time to answer and try to think backward. Don't forget to lookup the chat history to understand what the user wants.
You can't be lazy, NEVER! The user needs your help!

Internally, you can call the following functions:
- show_all_actions: use this function if the user wants to list all the actions
- delete_action: use this if the user wants to delete 1 or more actions
- action_info: use this if the user wants information about a single action
- create_action: use this if the user wants to create an action. If the eplicity asks for an html, use html_gen instead
- update_action: use this if the user watns to update or modify or improve an action
- html_gen: use this if the user wants to generate an html page
- crawler: use this if the user wants to crawl or scrape a web page
- tester: use this if the user wants to test an action
- grapher: use this if the user wants to create a chart or a graph
- db_store: use this if the user wants to store data inside the database

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