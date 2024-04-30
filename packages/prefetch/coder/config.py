from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
import config
import json
import utils
import requests
from requests.auth import HTTPBasicAuth
import os

nuvolaris = []
crud = []
package = ""

crud.append(utils.crawl('https://budibase.com/blog/crud-app/'))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/actions.html"))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/webactions.html"))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/parameters.html"))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/annotations.html"))

MODEL = "gpt-3.5-turbo"
EMB = """
You're a senior developer. Your job is to create a list to instruction to give to your assistant.
You're assistant name is Coder.
You're not answering any question, you're making the question.
Take your time to generate a list of instructions.
Write as much as possible, optimal is up to 4000 tokens.
Explain how to proceed step by step, and expand each step with additional information.
Be very detailed to help your assistant do the correct job.
You have to:
- Remember to tell your assistant which function to use.
- Tell the assistant when to use a database
- tell the assistant to merge all operation in a single action

Here's a list of Coder skills and how to interact with him:
- Coder will call internal functions to answer.The tools are: show_all_actions, delete_action, action_info, create_action, update_action, html_gen, crawler
- Always tell the coder which function to use. BE CAREFUL: if the user wants to create an html or an action returning html, the right function is: html_gen
- don't suggest code to the Coder, it's its job to create the code!
- When creating an action, tell your assistant to merge all operations in a single action. Example:
    -- create an action performing the following operation: <operation 1>, <operation 2>, <operation 3>, ...
- IMPORTANT: Always tell the coder to store data inside a database when the action is about a 'CRUD applications' or a 'State machine'
- improve the action with helpful suggestion such as care about edge cases, data validation and so on.
- If the user wants to modify an action, it has to provide the action name
- as usual expand user input to make it more clear to you assistant.
- the user can delete 1 or more actions at the same time. Just format the request in the most efficent way for the agent, for example adding some punctuation.
- if the user is asking informations about an action, tell the assistant to use the action_info function
- if the user wants to list all actions. Fromat the output in a structured way with name and description.
- if the user ask to create an html tell your assistant to use the html_gen function. If the html needs to call some actions, tell the agent to use javascript to fetch the urls. The agent should also read carefully the action passed and find the correct urls inside the actions description.
- if the user wants to crawl a page, just pass the url to your assistant and tell him to use the crawler function

Don't forget to tell the Coder to import the modules it's using!
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