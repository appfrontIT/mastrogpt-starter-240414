#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "an action which generate an action returning an HTML page"
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/grapher/bot

from openai import OpenAI
import requests
import config
import pandas as pd
import json
from requests.auth import HTTPBasicAuth

AI = None
MODEL = "gpt-4o"

def main(args):
    global AI
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    config.session_user = args.get('user', False)
    if not config.session_user:
        return {"statusCode": 404, "body": "failed to retrieve the user, please login again"}
    input = args.get("input", False)
    if not input:
        return {"statusCode": 400, "body": "error: no input provided"}
    data = args.get('data', None)
    if data == None:
        return {"StatusCode": 400, "body": "data is missing"}
    messages = [
        {"role": "system", "content": """You're a master of creating charts using chart.js API. Follow the user request and create an amazing graph! You have all the time you need, don't rush. YOU MUST USER CHARTJS TO MAKE THE GRAPH. To use chart.js you must import it in the following way: <script src='https://cdn.jsdelivr.net/npm/chart.js'>.
        Answer only and directly with the full html (starting from <!DOCTYPE html>), don't include the codeblock (```html)"""},
    ]
    messages.extend(input)
    messages.extend([{'role': 'user', 'content': "Here's the data you must use in your graph:\n"}])
    url = data.get('url', None)
    if url != None:
        response = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/utility/single_page_scrape',
                            json={'url': data.get('url')})
        if response.ok:
            messages.extend([{'role': 'user', 'content': f"data from url:\n{response.text}"}])
        else:
            return {"statusCode": 500, "body": "an error occured while fetching the url"}
    file = data.get('file', None)
    if file != None:
        file = file.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        s = requests.get(file, stream=True)
        if(s.ok):
            with open('./bdsfull_data.txt', 'wb') as fd:
                for chunk in s.iter_content(chunk_size=128):
                    fd.write(chunk)
        else:
            s.raise_for_status()
        chunksize = 500
        messages.extend([{'role': 'user', 'content': f"data from csv in chunk of size {chunksize}:\n"}])
        with pd.read_csv('./bdsfull_data.txt', chunksize=chunksize) as reader:
            for chunk in reader:
                messages.extend([{'role': 'user', 'content': f"chunk:\n{chunk}"}])
        # text_series_list = [df[col].astype(str) for col in df.columns]
        # text_strings = [' '.join(text_series) for text_series in text_series_list]
        # print(text_strings)
    text = data.get('text', None)
    if text != None:
        messages.extend([{'role': 'user', 'content': f"data from text:\n{text}"}])
    print(messages)
    response = AI.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    editor = {"function": response.choices[0].message.content, "description": '', "name": args.get('name', ''), "namespace": '', "package": '', "language": 'html'}
    requests.post("https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/db/load_message",
                auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]),
                json={'id': config.session_user['_id'], 'cookie': config.session_user['cookie'], 'message': {'output': response.choices[0].message.content, 'editor': editor}})
    return {"statusCode": 200, "body": { "output": response.choices[0].message.content } }