#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

from openai import OpenAI
import socket

AI = None
MODEL = "gpt-3.5-turbo"

ROLE="""
You're specialize in creating HTML page to test Nuvolaris action.
- You take an action as input and answer ONLY with the html page.
- The html page MUST use javascript to test the API call. If the action needs parameters, display a prompt to input them
- The endpoint will be provided with the action.
- If you don't get both information, you'll answer "I need the action uri and the action info to create the HTML"
- The action always returns: {"output": result}
- Display the action url on top of the page, in <h2> format, and a small description of the action below that
"""

def ask(
    query: str,
    model: str = MODEL,
    token_budget: int = 8192 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    messages = [
        {"role": "system", "content": ROLE},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
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
        output = output.replace('"', '&quot;')
        # print(output)

    res = { "output": output}
    return {"body": res }

