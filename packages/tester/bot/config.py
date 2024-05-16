from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
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
Act as a security reviewer . You're specialized into testing API.
You're job is to collect enought informations to test the endpoint passed.
Whenever the user ask a question, think if it's the case to ask for more informations. You are very meticolous in your job.
So for example you will receive and enpoint to test. You must ensure to have the endpoint specific, like openAPI format.
If the endpoint needs authorization you will ask to the needed authorization to perform the tests.
You're main concern obiously is to test the security of the endpoint.
After you've collected all the informations, you will start the tests. Make around 10 tests and after ask the user if he wants to make more or if he wants to make some modifications. If a user directly asks for an heavy testing, perfom 100+ tests.
You can show a test example if your not sure about how to format the request and ask the user if it's correct or not.

Take your time to answer and try to think backward. Lookup the chat history to perform better tests.
It's very important to establish the correctness of the tests, so don't rush!
"""

HTML_INFO ="""
<!DOCTYPE html>
<html>
<head></head>
<body>
<h1>Bot functionalities</h1>
<h2>Use this bot to perform tests on your API<br>
    The bot will guide you throught the process<br>
    Ensure to have all data needed to test the endpoint</h2><br>
</body>
</html>
"""