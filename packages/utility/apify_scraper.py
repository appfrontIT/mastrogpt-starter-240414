#--web false
#--kind python:default
#--annotation description "This action scrape a web page and all the links of the same domain inside the page. It stores data inside the database. If embedding is true, it also store the embedding array. Parameters: {"url": url, "embedding": true/false}"
#--param APIFY_ACTOR $APIFY_ACTOR
#--param APIFY_TOKEN $APIFY_TOKEN
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param JWT_SECRET $JWT_SECRET
#--annotation provide-api-key true
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/utility/apify_scraper

import jwt
from openai import OpenAI
import requests
import json
import re
from requests.auth import HTTPBasicAuth
import os

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
DECODED = None

def send_message(msg):
    global DECODED
    requests.post(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/db/load_message",
                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                json={'id': DECODED['id'], "message": {"output": msg}})

def extract_domain(url):
    # Define a regular expression pattern for extracting the domain
    pattern = r"(https?://)?(www\d?\.)?(?P<domain>[\w\.-]+\.\w+)(/\S*)?"
    # Use re.match to search for the pattern at the beginning of the URL
    match = re.match(pattern, url)
    # Check if a match is found
    if match:
    # Extract the domain from the named group "domain"
        domain = match.group("domain")
        return domain
    else:
        return None

def main(args):
    ACTOR = args.get('APIFY_ACTOR', '')
    TOKEN = args.get('APIFY_TOKEN', '')
    token = args.get('token', False)
    embedding = args.get('embedding', False)
    if ACTOR == '' or TOKEN == '' or not token:
        return {'statuCode': 500, "body": "internal server error"}
    url = args.get('url', '')
    if url == '':
        return {'statuCode': 400, "body": "parameter 'url' not found"}
    secret = args.get('JWT_SECRET')
    global DECODED
    DECODED = jwt.decode(token, key=secret, algorithms='HS256')
    obj = {
        "aggressivePrune": False,
        "clickElementsCssSelector": "[aria-expanded=\"false\"]",
        "clientSideMinChangePercentage": 15,
        "debugLog": False,
        "debugMode": False,
        "ignoreCanonicalUrl": False,
        "proxyConfiguration": {
            "useApifyProxy": True
        },
        "readableTextCharThreshold": 100,
        "removeCookieWarnings": True,
        "removeElementsCssSelector": "nav, footer, script, style, noscript, svg,\n[role=\"alert\"],\n[role=\"banner\"],\n[role=\"dialog\"],\n[role=\"alertdialog\"],\n[role=\"region\"][aria-label*=\"skip\" i],\n[aria-modal=\"true\"]",
        "renderingTypeDetectionPercentage": 10,
        "saveFiles": False,
        "saveHtml": False,
        "saveMarkdown": True,
        "saveScreenshots": False,
        "startUrls": [{ "url": url }],
        "useSitemaps": False
        }
    crawl = requests.post(f"https://api.apify.com/v2/acts/apify~website-content-crawler/run-sync-get-dataset-items",headers={"Content-Type": "application/json","Authorization": f"Bearer {TOKEN}"}, json=obj)
    if crawl.status_code != 201:
        send_message(f"É avvenuto un problema durante lo scraping. L'errore é:\ncode: {crawl.status_code}\nbody: {crawl.text}\nRiprovare o consultare Apify per comprendere la natura del problema")
        return {'statusCode': crawl.status_code, "body": crawl.text}
    obj_list = []
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    ROLE = """You're job is to summarize the text you receive.
    Answer only with the summarized text, nothing else must be returned.
    Don't write everything in the same row, format the output in a way is easier to read"""
    for dict in crawl.json():
        response = AI.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": ROLE},
                {"role": "user", "content": f"summarize the passed text:\n{dict['text']}"}
            ],
        )
        data = {
            "url": dict['url'],
            "text": dict['text'],
            "summary": response.choices[0].message.content
            }
        obj_list.append(data)
    collection = f"crawl_{extract_domain(url).replace('-', '_').replace('.', '__')}"
    send_message("Lo scraping é avvenuto con successo, procedo a salvare i dati nel database")
    response = requests.post(f"https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/db/mongo/{collection}/add_many",
                            headers={'Authorization': 'Bearer ' + token},
                            json={"data": obj_list})
    if response.ok:
        send_message(f"Collection {collection} salvata all'interno del database")
        if embedding:
            send_message("Procedo ad eseguire l'embedding degli elementi salvati")
            embed = requests.post(f'https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/embedding/embed',
                                auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]),
                                json={'collection': collection, 'token': token})
            if embed.ok:
                send_message("Embedding avvenuto correttamente")
            else:
                send_message("Errore: embedding non riuscito")
        return {'statusCode': 204}
    return {'statusCode': 500, 'body': "Could't store data in database"}
