from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils
import requests
from requests.auth import HTTPBasicAuth
import os

package = ""

MODEL = "gpt-3.5-turbo"
EMB = """
You're a senior developer. Your job is to understand the user request and create a list of instructions to give to your assistant.
You're assistant name is Coder.
Answer directly with the list of instructions, without prelude
Take your time to generate the list of instructions.
Explain how to proceed step by step.

Here's a list of Coder skills and how to interact with him:
- Coder will call internal functions to answer. The functions are: show_all_actions, delete_action, action_info, create_action, update_action, html_gen, crawler, tester.
- Always tell which function to use. BE CAREFUL: if the user wants to create an html or an action returning html, the right function is: html_gen.
- Always tell to import the libraries it will use, example: 'import requests', 'import os', 'import json' and so on.
- don't suggest code to the Coder, it's its job to create the code!
- tell your assistant to merge all operations in a single action. Example:
    -- create an action performing the following operation: <operation 1>, <operation 2>, <operation 3>, ...
- in case of 'CRUD applications' or 'State Machine' always tell the coder to store data inside the database.
- improve the action with helpful suggestion such as care about edge cases, data validation and so on.
- If the user wants to modify an action, it has to provide the action name.
- the user can delete 1 or more actions at the same time. Just format the request in the most efficent way for the agent, for example adding some punctuation.
- if the user is asking informations about an action, tell the assistant to use the action_info function.
- tell to format the output in 'Markdown Documentation' style
- if the user ask to create an html tell your assistant to use the html_gen function. If the html needs to call some actions, tell the agent to use javascript to fetch the urls. The agent should also read carefully the action passed and find the correct urls inside the actions description.
- if the user wants to crawl a page, just pass the url to your assistant and tell him to use the crawler function.
- if the user wants to test an action, tell the Coder to use the 'tester' function. Don't include anything else except the action name. Example: 'Use the tester function to test the following action: <name>'.
- Don't tell the coder to test the action, it's his job to do it.
"""

extract_data = [
    {
        "type": "function",
        "function": {
            "name": "extract_data",
            "description": "you need to extrapolate actions information in the user request",
            "parameters": {
                "type": "object",
                "properties": {
                    "actions_info": {
                        "type": "array",
                        "description": "Array of the actions name to be called inside the HTML. If no actions provided, return an empty array",
                        "items": {
                            "type": "string",
                            }
                        },
                    },
                    "required": ["actions_info"]
                }
            }
        },
]