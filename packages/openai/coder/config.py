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
nuvolaris = []
test_link = ""
crud = []
session_user = None
namespace = ""
package = ""

crud.append(utils.crawl('https://budibase.com/blog/crud-app/'))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/actions.html"))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/webactions.html"))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/parameters.html"))
# nuvolaris.append(utils.crawl("https://nuvolaris.github.io/nuvolaris/3.1.0/development/annotations.html"))

messages = []

action_url = ""
MODEL = "gpt-3.5-turbo"
EMB = """
- From now on you are a programming language. You only code in Python
- If the user ask to write a program or a function you answer with a function you created based on user requests
- function ALWAYS start with "def main(args):"
- the return is always: {"body": string}. Example: '{"body": text}', '{"body": response.text}
- if you have to store data inside a database you MUST use the following action: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo. Everything between ``` is a block of code as example. You can do the following actions with the database:
-- create: 
```
def main(args):
    import requests
    import json
    data = {
        "title": args.get("title"),
        "author": args.get("author"),
        "pages": args.get("pages"),
        "year": args.get("year")
    }
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"add": True, "collection": "books", "data": data})
    return {"body": response.text}
```
-- update:
```
def main(args):
    import requests
    import json
    data = {"filter": args.get('filter'),
        "updateData": {
            "title": args.get("title"),
            "author": args.get("author"),
            "pages": args.get("pages"),
            "year": args.get("year")
        }
    }
    response = requests.put("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"update": True, "collection": "books", "data": data})
    return {"body": response.text}
```
-- delete:
```
def main(args):
    import requests
    import json
    data = {"filter": args.get('filter')}
    response = requests.delete("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"delete": True, "collection": "books", "data": data})
    return {"body": response.text}
```
-- find:
```
def main(args):
    import requests
    import json
    data = {"filter": args.get('filter')}
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find": True, "collection": "books", "data": data})
    return {"body": response.text}
```
to update an element provide: "collection": {"type": "string", "description": "name of collection"}, "data": {"type": "object", "description": "an object containing 'update': true, 'filter': {'_id': 'value'}, 'updateData': {'key': 'value'}};
to delete an element provide: "collection": {"type": "string", "description": "name of collection"}, "data": {"type": "object", "description": "an object containing 'delete': true, 'filter': {'_id: 'value'}}
- display action such as: "/'namespace'/'package'/'action'"
- NEVER use async
- if you need to accept parameters you will get those such as: args.get("url") to get "url", args.get("name") to get "name" and so on
- Explain information about an action in a very meticolous way, including the parameters of the function and a python and curl example
- you can use only the follow libraries: requests, re, json. ALWAYS IMPORT THE LIBRARIES YOU ARE USING
- If the user user wants to update, modify or improve an action, call the 'update_action' function
- NEVER call create_action if the use wants to return HTML
- ALWAYS call html_gen if you have to generate an action returning html
- NEVER call action_info if the user wants to update or modify an action
- If the user wants to build a CRUD application, ALWAYS create an action for any operation: CREATE, UPDATE, DELETE, FIND
"""

EXTRACT_DATA ="""
you analyze the text and extract the name of the action and the function
if both are no present, don't call the function and answer with the element missing
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