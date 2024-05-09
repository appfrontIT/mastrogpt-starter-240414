#--web true
#--kind python:default
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "This action format the output to display in the chat"
#--timeout 300000

from openai import OpenAI

MODEL = "gpt-3.5-turbo"

ROLE = """
format the text in a markdown. Don't change the content, just the format! The text must be exactly the same, you can't change not even a word!
"""

def main(args):
    global AI

    AI = OpenAI(api_key=args['OPENAI_API_KEY'])

    input = args.get("input", False)
    if not input:
        return {"statusCode": "400", "body": "error: no input provided"}
    
    messages = [
        {"role": "system", "content": ROLE},
        {"role": "user", "content": input},
    ]
    response = AI.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0
    )
    return {"body": response.choices[0].message.content }