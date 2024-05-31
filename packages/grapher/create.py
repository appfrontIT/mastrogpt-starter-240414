#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which generate an action returning an HTML page"
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/grapher/create

from openai import OpenAI
import requests

AI = None
MODEL = "gpt-3.5-turbo"

def main(args):
    global AI

    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    input = args.get("input", False)
    if not input:
        return {"statusCode": "400", "body": "error: no input provided"}
    messages = [
        {"role": "system", "content": "You're a master of creating charts using chart.js API. Follow the user request and create an amazing graph! You have all the time you need, don't rush. YOU MUST USER CHARTJS TO MAKE THE GRAPH. To use chart.js you must import it in the following way: <script src='https://cdn.jsdelivr.net/npm/chart.js'>. Answer only and directly with the full html (starting from <!DOCTYPE html>)"},
        {"role": "user", "content": input},
    ]
    response = AI.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return {"body": response.choices[0].message.content }