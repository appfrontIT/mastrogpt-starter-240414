from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
from requests.auth import HTTPBasicAuth
import os

html = ""
session_user = None

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

MODEL = "gpt-3.5-turbo"

ROLE = """
You're the administrator of a serverless application.
You have to call the correct function based on the user request:
- create_user: The admin wants to create an user. This action needs: name, password, role.
- update_user: the admin wants to update an user. This action needs: name, role.
- delete_user: the admin wants to delete an user. Thi action needs: id

Take your time to answer, don't rush. Think carefully when you have to call a function
If the admin is asking for anything else, answer with a list of your functionality.
"""
