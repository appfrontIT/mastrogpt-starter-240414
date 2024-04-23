#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY
#--annotation description "an action which generate an action returning an HTML page"

from openai import OpenAI
import bot_functions
import requests
import config

AI = None
MODEL = "gpt-3.5-turbo"

def ask(
    query: str,
    model: str = MODEL,
) -> str:
    # expand = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/prefetch/html', json={"input": query})
    # print(expand)
    messages = [
        {"role": "system", "content": config.ROLE},
        {"role": "user", "content": f"create an HTML implementing the following request.\nRequest:\n{query}"},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

TUNED_MODEL = None

def main(args):
    global AI

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    input = args.get("input", "")
    print(input)
    output = ""
    if input == "":
        output = "Please provide an action to generate the html"
    else:
        output = ask(query=input, model=MODEL)
        output = output.replace("```html", '')
        output = output.replace("```", '')
        print(output)
        # output = output.replace('"', '&quot;')

    res = { "output": output}
    return {"body": res }

