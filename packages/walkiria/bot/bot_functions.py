from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from typing import List
from bs4 import BeautifulSoup
import requests
import os
from requests.auth import HTTPBasicAuth
import json
import config, utils
from chart import grapher
from tester import tester
import bs4
import lxml
from datetime import datetime
import base64
import chart

MODEL="gpt-4o"

def embed_collection(collection = None):
    if collection == None:
        return 'no collection provided'
    embed = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/embedding/embed',
                        auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                        json={'collection': collection, 'token': config.session_user['JWT']})
    if embed.ok:
        return "embedding succesfull on collection " + collection
    return "embedding failed. Error: " + embed.text

def google_for_answers(url = None):
    if url == None:
        return "No url provided"
    socs_cookie = base64.encodebytes(f"\b\x01\x12\x1C\b\x01\x12\x12gws_{datetime.today().strftime('%Y%m%d')}-0_RC3\x1A\x02en \x01\x1A\x06\b\x80º¦±\x06".encode())
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/123.0.2420.97",
        "Cookie": f"SOCS={socs_cookie}",
    }
    response = requests.get(url + "&hl=it&filetype=HTML", headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    divTag = soup.find_all("div", {"id": "search"})
    ret = []
    for tag in divTag:
        tdTags = tag.find_all('a', href=True)
        for tag in tdTags:
            if (tag['href'].find('https://www.youtube.com/')) == -1 and (tag['href'].find('https://www.amazon.it/')) == -1 and (tag['href'].find('https://transalte/')) == -1 and (tag['href'].find('/search?')) == -1:
                # tmp = f"url: {tag['href']}\n" + single_page_scrape(tag['href'])
                # tmp_token = utils.num_tokens(tmp)
                # if (max_token - tmp_token) < 0:
                #     break
                # ret.append(tmp)
                # max_token = max_token - tmp_token
                ret.append(tag['href'])
    if len(ret) > 0:
        to_str = ', '.join(ret)
        return f"Here a list of the page to scrape: {to_str}.\nScrape each page one at a time, than answer on everyone"
    return "nessun risultato"

def domain_scraping(url = '', embedding = False):
    if url == '':
        return "No url provided"
    resp = requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/utility/apify_scraper",
                        auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                        json={"url": url, "embedding": embedding, "token": config.session_user['JWT']})
    return "the scraping is processing, it will be performed in background since it may takes some time"

def single_page_scrape(url = None):
    if url == None:
        return "no url provided"
    response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/single_page_scrape',
                            json={'url': url})
    return response.text

def html_gen(args):
    actions_info = args.get('actions_names', '')
    description: str = args.get('description', '')

    name: str = args.get('name', '')
    action_array = []
    for action in actions_info:
        action_array.append(action_info(action['name'], action['package']))
        # status = utils.action_info(action['name'], action['package'])
        # if status.status_code == 200:
        #     obj = status.json()
        #     action_array += f"name: {obj['name']}\n"
        #     annotations = obj['annotations']
        #     for pair in annotations:
        #         if pair['key'] == 'url' or pair['key'] == 'description':
        #             action_array += f"{pair['key']}: {pair['value']}\n"
        #     action_array += f"code: {obj['exec']['code']}\n"
        # else:
        #     return f"the following action does not exists: {action}\n"
        
    if action_array != "":
        query = f"{description}\nHere the informations about the actions you have to call inside it: {action_array}"
    else:
        query = description
    html = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/html_gen/bot",
                        json={"input": query, "name": name, 'id': config.session_user['id']})
    if html.status_code == 204:
        return "failed to generate the HTML"
    return "Page created"

def update_action(function = False, fix = False):
    if function and fix:
        query = f"apply this fix to the following function.\nfix: {fix}\n\nfunction:{function}"
        response = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/generate?blocking=true',
                            auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                            json={"request": query, "token": config.session_user['JWT']})
        return response.text
    return "there was an error performing this operation"

def create_action(query):
    response = requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/walkiria/generate?blocking=true',
                            auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                            json={"request": query, "token": config.session_user['JWT']})
    return response.text

def store_text_in_specific_format(url, collection, format):
    return requests.post('https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/db_store_init', auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={
        "url": url,
        "collection": collection,
        "format": format,
        "token": config.session_user['JWT']
    }).text

def action_info(name = False, package = False):
    if not name or not package:
        return "Ho bisogno sia del nome che del package per recuperare l'azione"
    if package not in config.session_user['package'] and config.session_user['role'] != 'admin':
        return "Non sei autorizzato ad accedere a questa azione"
    action = utils.action_info(name, package)
    if action.status_code == 200:
        obj = action.json()
        description = ''
        returns = ''
        for an in obj['annotations']:
            if an['key'] == 'description':
                description = an['value']
            elif an['key'] == 'return':
                returns = an['value']
        if obj['exec']['binary'] == True:
                function = "il corpo del codice non é recuperabile, perché l'azione incorpora piú file "
        else:
            function = obj['exec']['code']
        return f"Action:\nfunction: {function}, name: {obj['name']}, description: {description}, return: {returns}, package: {package}"
    return "Non sono riuscito a trovare l'azione richiesta. Assicurati che il nome sia corretto e che sia specificato il package se appartiene ad uno"

def delete_action(name = False, package = False):
    if not name or not package:
        return "Ho bisogno del nome e del package per eliminare l'azione"
    if package not in config.session_user['package'] and config.session_user['role'] != 'admin':
        return "Non sei autorizzato ad accedere a questa azione"
    response = utils.delete_action(name, package)
    delete = requests.delete('https://nuvolaris.dev/api/v1/web/gporchia/base/openAPI/delete',
            headers={'Authorization': 'Bearer ' + config.session_user['JWT']},
            json={'action': f"""url: https://nuvolaris.dev/api/v1/web/gporchia/{package}/{name}"""})
    return f"status: {response.status_code}, body: {response.json()}"

def get_actions():
    actions_list = utils.get_actions().json()
    action_arr = []
    for action in actions_list:
        action_arr.append(action)
    name_arr = []
    for x in action_arr:
        x.pop('limits')
        x.pop('publish')
        x.pop('updated')
        x.pop('version')
        x.pop('exec')
        annotations = []
        for an in x['annotations']:
            if an['key'] == 'description' or an['key'] == 'url':
                annotations.append(an)
        x['annotations'] = annotations
        package = x['namespace'].split('/')[1]
        x.pop('namespace')
        x['package'] = package
        name_arr.append(x)
    return f"Here are all the available actions:\n{name_arr}"

def show_all_actions():
    actions_list = utils.get_actions().json()
    action_arr = []
    for action in actions_list:
        if config.session_user['role'] == 'admin':
            action_arr.append(action)
        else:
            package = action['namespace'].split('/')[1]
            if package in config.session_user['package']:
                action_arr.append(action)
    name_arr = []
    for x in action_arr:
        x.pop('limits')
        x.pop('publish')
        x.pop('updated')
        x.pop('version')
        x.pop('exec')
        annotations = []
        for an in x['annotations']:
            if an['key'] == 'description' or an['key'] == 'url':
                annotations.append(an)
        x['annotations'] = annotations
        name_arr.append(x)
    return f"""display all the following actions.\nActions:\n{name_arr}\nYou must display the actions in this output: namespace: <namespace>\nname: <name>\ndescription; <description>"""

def verify(analyses):
    return analyses

def send_message(message):
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], "message": {"output": message}})
    return 'message sent'

def tools_func(
        messages: list[dict[str, str]],
        response: ChatCompletion
        ):
    # requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]), json={'id': config.session_user['_id'], "message": {"output": "Certo, procedo subito con la tua richiesta"}})
    while True:
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)
        for tool_call in tool_calls:
            print(tool_call.function.name)
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                **function_args
                )
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })
        response = config.AI.chat.completions.create(model='gpt-4o', messages=messages, tools=tools, tool_choice="auto", temperature=0.1, top_p=0.1)
        if response.choices[0].finish_reason != "tool_calls":
            break
        # requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
        #             auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
        #             json={'id': config.session_user['_id'], "message": {"output": "Sto elaborando la tua richiesta, per favore attendi"}}
        #             )
    return response.choices[0].message.content


available_functions = {
    "show_all_actions": show_all_actions,
    "delete_action": delete_action,
    "update_action": update_action,
    "action_info": action_info,
    "create_action": create_action,
    "html_gen": html_gen,
    "domain_scraping": domain_scraping,
    "tester": tester,
    "grapher": chart.grapher,
    # "store_text_in_specific_format": store_text_in_specific_format,
    "verify": verify,
    "get_actions": get_actions,
    "send_message": send_message,
    "single_page_scrape": single_page_scrape,
    "google_for_answers": google_for_answers,
    "embed_collection": embed_collection
}

tools = [
        {
        "type": "function",
        "function": {
            "name": "update_action",
            "description": """You must update the provided code according to the user request""",
            "parameters": {
                "type": "object",
                "properties": {
                    "function": {"type": "string", "description": "the full function code"},
                    "fix": {"type": "string", "description": "one or more fix to apply on the code"}
                    },
                "required": ["function", "fix"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "show_all_actions",
            "description": """the user want to display or list all the actions""",
            "parameters": {
                "type": "object",
                "properties": {},
                    "required": [],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "create_action",
            "description": "create an action",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "all the informations about the action to create"},
                    },
                    "required": ["query"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "delete_action",
            "description": "the user wants to delete an action",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "the action name to be deleted"},
                    "package": {"type": "string", "description": "the action package"}
                    },
                    "required": ["name", "package"],
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "action_info",
            "description": "the user wants information about an action or how to use it",
            "parameters": {
                "type": "object",
                "properties": {
                    "name" : {"type": "string", "description": "the name of the action, it must be 1 word"},
                    'package': {"type": "string", "description": "the package of the action"}
                    },
                    "required": ["name", "package"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "html_gen",
            "description": "the user asks to create an action returning HTML, or the user wants an HTML page",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "action name"},
                            "description": {"type": "string", "description": "detailed description of the action to create"},
                            "actions_names": {
                                "type": "array",
                                "description": "Array of the actions name to be called inside the HTML. If no actions provided, return an empty array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "action name"},
                                        "package": {"type": "string", "description": "the package of the action"}
                                    }
                                    }
                                },
                            },
                            "required": ["name", "description", "actions_names"]
                        },
                    },
                    "required": ["args"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "domain_scraping",
            "description": "the user wants information about a web page or explicity ask to crawl a domain. Don't call this action if the user wants to store data inside the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "the url to crawl"},
                    "embedding": {"type": "boolean", "description": "True in case the user asks to embed data of the url, False otherwise"}
                    },
                    "required": ["url", "embedding"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "tester",
            "description": "the user wants to test an action giving the name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "the action name to test"},
                    'package': {"type": "string", "description": "the package of the action"}
                    },
                    "required": ["name"]
                }
            }
        },
        {
        "type": "function",
        "function": {
            "name": "grapher",
            "description": "the user wants to generate a graph or chart",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "the user specific request"},
                    "name": {"type": "string", "description": "name of the action to generate. it must ends with '_chart'"},
                    "description": {"type": "string", "description": "a short description of the chart"},
                    "type": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string", "description": "data to visualize inside the chart"},
                            "collection": {"type": "string", "description": "the collection where to get the data from"},
                            }
                        }
                    },
                    "required": ["request", "name", "description", "type"]
                }
            }
        },
        # {
        # "type": "function",
        # "function": {
        #     "name": "store_text_in_specific_format",
        #     "description": "the user wants to store data from an url inside the database, following a specific format.",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "url": {"type": "string", "description": "the url of the file to store in the database"},
        #             "collection": {"type": "string", "description": "the collection where to store the data inside the database in snake_case. This should't include the 'collection' prefix"},
        #             "format": {"type": "string", "description": "how the data must be stored in pair of key value. Must be in markdown format"},
        #             },
        #             "required": ["url", "collection", "format"]
        #         }
        #     }
        # },
        {
            "type": "function",
            "function": {
                "name": "verify",
                "description": "verify the action generated. If you think the action is malformed or incorrect, update the action with your suggestions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analyses": {"type": "string", "description": "your feedbacks about the action"}
                    },
                    "required": ["analyses"],
                },
            }
        },
        {
        "type": "function",
        "function": {
            "name": "get_actions",
            "description": """You want to lookup to all the actions to check if there is one suitable to be incorporated in your code""",
            "parameters": {
                "type": "object",
                "properties": {},
                    "required": [],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Message to send to the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "an update on your making"}
                    },
                    "required": ["message"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "single_page_scrape",
                "description": """scrape a single page skipping all sublinks and extract text. Use this if you the user ask for informations or summary about a page.
                You can also use this function for yourself, by asking the user a webpage where you can gather informations to answer the question""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "the url to scrape"}
                    },
                    "required": ["url"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "google_for_answers",
                "description": "Search Google with fully-formed http URL to enhance knowledge.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "the whole google url plus the query parameter"}
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "embed_collection",
                "description": "perform embedding on all elements of the collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection": {"type": "string", "description": "the name of the collection"}
                    },
                    "required": ["collection"]
                }
            }
        }
]