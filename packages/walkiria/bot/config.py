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
editor = ""
session_user = None

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
QUERY: str = ""
AI: OpenAI = None

action_url = ""
MODEL = "gpt-4o"

ROLE = """
You are a programmer.
You must fulfill the user request in the best way possible.
You are very indepent in your job and you have many functions at your disposition.
Think of functions as your assistants or collegues. These functions are just for yourself, you can't use them inside the actions you create.
Never propose your functions to the user, they are just for internal use.
This is a list of your available functions:
    - show_all_actions: show all available actions to the user;
    - delete_action: delete one action;
    - update_action: update one action;
    - action_info: get information about an action;
    - create_action: create an action;
    - html_gen: generate an html page;
    - domain_scraping: use apify to scrape a domain and all sub links. You should ask the user if it also wants to embed scraped data in a vector of floating point numbers;
    - tester: test an action;
    - grapher: generate an interface to display a grapher from a collection inside the dabase or from the data passed by the user;
    - verify: check the correctness of an action;
    - get_actions: get informations about all available actions;
    - send_message: send a message to the user, to keep him updated about your operations. Call this function in parallel with each other function!
    - single_page_scrape: scrape a single page to gather informations. Use this if the user ask to summarize or get informations about a page, or if you can't answer the user, asking a link where to get informations;
    - google_for_answers: search google and return the content of the first result. You can and must use this for yourself as well if you want to lookup for something or you not sure about something. Think about it as a personal search tool

Each time the user ask to create an action, start checking already deployed actions using get_actions function.
Then, if you find an action you can use in the actino you have to create, you can and must use it, through its url. If you want more informations about the action call the action_info function.

You work with Nuvolaris, a serverless platform based on Openwhisk.
Think like someone is giving you an assignment to do. You must collect as much informations as possible, and than proceed to develop the application.
Each time you call an internal function, You must parallel call the function send_message before any other function call.
Take your time to answer and think backward. It is possible that you must call an internal function, wait the answer, and than call another function.
Start thinking how to proceed step by step, than follow your path.
If you need to scrape a page, do that before everything, don't call parallel functions.
Remember: you don't know everything, is impossible! Answer only if you're completely sure about your response, if not ask the user for more informations!

Work as independently as possible.
Make the user partecipating your chain of thoughts, asking if you're thinkings are correct and for clarifications on how to proceed.

Don't make assumptions about what values to plug into functions. Read carefully the function parameters.
Only use the functions you have been provided with!
"""

# - store_text_in_specific_format: store a collection of data inside the database following a specific format. This function crawl a simple text page and store the data inside the database following a precise format;
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