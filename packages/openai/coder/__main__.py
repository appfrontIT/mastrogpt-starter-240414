#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

from openai import OpenAI
import config
import bot_functions

AI = None
MODEL = "gpt-3.5-turbo"

messages=[{"role": "system", "content": config.EMB}]

def ask(
    query: str,
    model: str = MODEL,
    token_budget: int = 8192 - 500,
    print_message: bool = False,
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    messages = [
        {"role": "system", "content": config.EMB},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
        tools=bot_functions.tools,
        tool_choice="auto"
    )
    # We start checking if the tools activated. If not we answer generic question about Nuvolaris
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls
        return bot_functions.tools_func(AI, tool_calls, messages, response)
    print("no tools")
    return "Error, something went wrong in creating your action"

TUNED_MODEL = None

def main(args):
    global AI
    global TUNED_MODEL
    config.html = config.HTML_INFO

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    TUNED_MODEL = MODEL

    input = args.get("input", "")
    if input == "":
        res = {
            "output": "Benvenuti in Walkiria, la piattaforma AI di Appfront.",
            "title": "OpenAI Chat",
            "message": "You can chat with OpenAI.",
        }
    elif input[len(input) -1] == ' ':
        return {"body": {"output": ""}}
    else:
        output = ask(query=input, print_message=False, model=TUNED_MODEL)
        res = {
            "output": output
        }
    if config.html != "":
        res['html'] = config.html
    return {"body": res }
