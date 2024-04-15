#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which generate an action returning an HTML page"

from openai import OpenAI
import bot_functions

AI = None
MODEL = "gpt-3.5-turbo"

ROLE="""
You're specialize in creating HTML page. You answer returning the HTML. NOTHING ELSE MUST BE RETURNED
- Answer ONLY with the html page.
- write to your max_tokens
- If you need to make a request to an endpoint you MUST use javascript
- If you need to perform a DELETE or UPDATE action, always use 'filter: {{id: id}}'
- If you need to perform a find or search action, filter all model fields
- If there are requests, make a div to display the return of the API call.
- include this into the head:
<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
<style>
* { box-sizing: border-box; }
body {font-size: 80%;}
nav {
  float: left;
  width: 30%;
  background: #ccc;
  padding: 20px;
}
article {
  float: left;
  padding: 20px;
  width: 70%;
  background-color: #f1f1f1;
  height: 100%;
}
section::after {
  content: "";
  display: table;
  clear: both;
}
</style>
<style>undefined</style><link rel="preconnect" href="https://fonts.googleapis.com" crossorigin="use-credentials"><link rel="preconnect" href="https://fonts.gstatic.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mulish:wght@200;300;400;500;600;700;800;900&amp;display=swa">
- ALWAYS answer directly with <!DOCTYPE html>. No starting quotes
"""

def ask(
    query: str,
    model: str = MODEL,
    print_message: bool = False,
) -> str:
    messages = [
        {"role": "system", "content": ROLE},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto",
    )
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(AI, tool_calls, messages, response)
    print("not tools")
    return response.choices[0].message.content

TUNED_MODEL = None

def main(args):
    global AI

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    input = args.get("input", "")
    output = ""
    if input == "":
        output = "Please provide an action to generate the html"
    else:
        output = ask(query=input, print_message=False, model=MODEL)
        output = output.replace("```html", '')
        output = output.replace("```", '')
        # output = output.replace('"', '&quot;')

    res = { "output": output}
    return {"body": res }

