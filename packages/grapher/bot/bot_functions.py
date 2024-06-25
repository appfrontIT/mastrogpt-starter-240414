import config
import requests
import json
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from requests.auth import HTTPBasicAuth

def db_query(collection = None):
    dbname = config.CLIENT['mastrogpt']
    collection_list = dbname.list_collection_names()
    
    if collection in collection_list:
        db_coll = dbname[collection]
    else:
        return "collection provided does not exists"
    data = db_coll.find({}, {'_id': 0}).limit(10)
    return "\n".join(str(el) for el in list(data))

def gathering_data_from_url(url = None):
    if url != None:
        response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/single_page_scrape', json={'url': url})
        if response.ok:
            return response.text
        else:
            return "an error occured while fetching the url"

def gathering_data_from_text(text = None):
    return text

def generate_graph(name, request, collection = '', text = '', url = ''):
    messages = [
        {"role": "system", "content": """You're a master of creating charts using chart.js API. Follow the user request and create an amazing graph! You have all the time you need, don't rush. YOU MUST USER CHARTJS TO MAKE THE GRAPH.
        To use chart.js you must import it in the following way:
            <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js/dist/chart.umd.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>.
        Answer only and directly with the full html (starting from <!DOCTYPE html>).
        NEVER include the codeblock (```html).
        Also, remember to display the error in case something is going wrong!"""},
    ]
    messages.extend([{'role': 'user', 'content': request}])
    messages.extend([{'role': 'user', 'content': "Here's the data you must use in your graph:\n"}])
    if url != '':
        response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/single_page_scrape',
                            json={'url': data.get('url')})
        if response.ok:
            messages.extend([{'role': 'user', 'content': f"data from url:\n{response.text}"}])
        else:
            return {"an error occured while fetching the url"}
    if text != '':
        messages.extend([{'role': 'user', 'content': f"data from text:\n{text}"}])
    if collection != '':
        dbname = config.CLIENT['mastrogpt']
        collection_list = dbname.list_collection_names()
        if collection in collection_list:
            db_coll = dbname[collection]
        else:
            return {"collection provided does not exists"}
        data = db_coll.find({}, {'_id': 0}).limit(10)
        messages.extend([{'role': 'user', 'content': f"""You must call this endpoint to fetch data from database, adding the fields you want to return: 'https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/{collection}/find_many?fields=' + encodeURIComponent(JSON.stringify(<fields to return>)).
                        Pay attention to the field you want to return because the name of the key MUST BE EXACTLY EQUAL, so you must be carefull with lowercase or uppercase letters.
                        This endpoint require authorization, here's a full example on how to get the token:
                            - let cookie = document.cookie; if (!cookie) return window.location.assign('/login');
                            - response = await fetch('https://nuvolaris.dev/api/v1/web/gporchia/base/auth/token?cookie=' + cookie, {{method: 'GET'}});
                            - if (response.ok) {{ const obj = await response.json(); const token = obj['token']}}
                        When calling the db, include the token as a Bearer: {{"Authorization": "Bearer " + token}}
                        Here's a list of the firsts 10 records of the collection:\n{list(data)}\n
                        You must than filter the data and use it in the chart"""}])
    response = config.AI.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    print(response.choices[0].message.content)
    editor = {"function": response.choices[0].message.content, "description": '', "name": name, "namespace": '', "package": '', "language": 'html'}
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'message': {'output': response.choices[0].message.content, 'editor': editor}})
    config.showEditor = True
    return response.choices[0].message.content

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
            print(function_response)
        response = config.AI.chat.completions.create(model='gpt-4o', messages=messages, tools=tools, tool_choice="auto", temperature=0.1, top_p=0.1)
        if response.choices[0].finish_reason != "tool_calls":
            break
        # requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
        #             auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
        #             json={'id': config.session_user['_id'], "message": {"output": "Sto elaborando la tua richiesta, per favore attendi"}}
        #             )
    return response.choices[0].message.content

available_functions = {
    "db_query": db_query,
    "gathering_data_from_url": gathering_data_from_url,
    "gathering_data_from_text": gathering_data_from_text,
    "generate_graph": generate_graph,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "db_query",
            "description": "a description of the query to make to the database. This function will returns the first 10 records of the collections",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection": {"type": "string", "description": "the collection where to perform the query"},
                },
                "required": ["collection"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gathering_data_from_url",
            "description": "scrape a page and gather the informations to use in the graph",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "the url to scrape to get the informations"},
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gathering_data_from_text",
            "description": "read the text and gather the informations to use in the graph",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "the text to read to get the informations"},
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_graph",
            "description": "after collecting all the data generate the graph",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "the name to give to the page"},
                    "collection": {"type": "string", "description": "the collection inside the database where to gather the data"},
                    "url": {"type": "string", "description": "the url to scrape where to get the data"},
                    "text": {"type": "string", "description": "plain text where to get the data"},
                    "request": {"type": "string", "description": "the user request on how to build the graph"}
                },
                "required": ["name", "request"]
            }
        }
    }
]