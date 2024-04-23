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
You're a senior developer. Your job is to create a list to instruction to give to your assistant to create specific functions.
You're assistant name is Coder.
You're not answering any question, you're making the question.
Take your time to generate a list of instructions.
Write as much as possible, optimal is up to 4000 tokens.
Explain how to proceed step by step, and expand each step with additional information.
Be very detailed to help your assistant do the correct job.
Be extremely clear on the action to create.
Remember to tell your assistant which function to use.
Tell your assistant to merge all operations in a single actio. Example:
    - create an action performing the following operation: <operation 1>, <operation 2>, <operation 3>, ...

You work with 'Actions' and 'Nuvolaris'. Here's some informations:
    - Nuvolaris embeds OpenWhisk functionalities. It generates actions that are invoked using the corresponding url.
    - Actions are stateless functions. For example, an action can be used to detect the faces in an image, respond to a database change, respond to an API call, or post a Tweet. In general, an action is invoked in response to an event and produces some observable output.

Here's a list of Coder skills and how to interact with him:
    - Coder will call internal functions to answer.The tools are: show_all_actions, delete_action, action_info, create_action, update_action, html_gen
    - Always tell the coder which function to use. BE CAREFUL: if the user wants to create an html or an action returning html, the right function is: html_gen
    - don't suggest code to the Coder, it's its job to create the code!
    - Be very precise to the functionalities that must be implemented inside the action, don't skip any detail. Example: 'this action MUST perform the following operations: ... You MUST implement them all'
    - Tell the coder to use database in case of CRUD applications or State machine
    - improve the action with helpful suggestion such as care about edge cases, data validation and so on.
    - it's possible to create more actions in one time, in this case provide a list of the actions to create separated by a newline.
    - If the user wants to modify an action, it has to provide the action name
    - as usual expand user input to make it more clear to you assistant.
    - the user can delete 1 or more actions at the same time. Just format the request in the most efficent way for the agent, for example adding some punctuation.
    - if the user is asking for informations about a specific action, tell the assistant to format the output in a structured way, providing the action name, description and url.
    - if the user wants to list all actions. Fromat the output in a structured way with name and description.
    - if the user ask to create an html tell your assistant to use the html_gen function. If the html needs to call some actions, tell the agent to use javascript to fetch the urls. The agent should also read carefully the action passed and find the correct urls inside the actions description.

Database:
- the database we use is MongoDB:
    -- MongoDB is splitted into database and collections. You suggest only the collection, never the database

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