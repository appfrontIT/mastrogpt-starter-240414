#--web false
#--kind python:default
#--annotation description "This action scrape a web page and all the links of the same domain inside the page. It stores data inside the database. If embedding is true, it also store the embedding array. Parameters: {"url": url, "embedding": true/false}"
#--param APIFY_ACTOR $APIFY_ACTOR
#--param APIFY_TOKEN $APIFY_TOKEN
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--timeout 300000

from openai import OpenAI
import requests
import json
import re

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
    embedding = args.get('embedding', False)
    print(embedding)
    if ACTOR == '' or TOKEN == '':
        return {"body": "error: couldn't get the credentials to use Apify"}
    url = args.get('url', '')
    if url == '':
        return {"body": "you need to pass an url to use this action"}
    
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
        return {"body": "error crawling the desidered link"}
    obj_list = []
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    ROLE = """You're job is just to explain the text received.
    Format your output including a Title for each section and a description. Example: "**This is the title**\nHere you will put the desctiption.\n\n**Another title**\nAnother description" and so on.
    Take your time to answer, it's very important that the text is outputted in a very smart and comprehensible way.
    Answer only with the explaination text, nothing else must be returned."""
    ret = ""
    for dict in crawl.json():
        response = AI.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ROLE},
                {"role": "user", "content": f"explain me the following text:\n{dict['text']}"}
            ],
        )
        ret += f"url:{url}\nsummary:{response.choices[0].message.content}\n\n"
        if embedding:
            embedded_response = AI.embeddings.create(model="text-embedding-3-small", input=response.choices[0].message.content)
            embedded_data = embedded_response.data[0].embedding
            data = {
            "url": dict['url'],
            "text": dict['text'],
            "summary": response.choices[0].message.content,
            "embedding": embedded_data
            }
        else:
            data = {
                "url": dict['url'],
                "text": dict['text'],
                "summary": response.choices[0].message.content
                }
        obj_list.append(data)
    db_data = {
            "insert_many": True,
            "collection": f"crawl_{extract_domain(url).replace('-', '_').replace('.', '__')}",
            "data": obj_list
        }
    response = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json=db_data)
    return {"body": ret}
