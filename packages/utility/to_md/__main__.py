#--web true
#--kind python:default
#--annotation description "This action convert a pdf into a markdown string"
#--timeout 300000
#--annotation url https://walkiria.cloud/api/v1/web/gporchia/utility/to_md

import requests
import urllib.request
import io
from pdfminer.high_level import extract_text

def convert_to_markdown(text):
    lines = text.split("\\\\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.isupper() and len(stripped) < 50:
            lines[i] = f"## {stripped}"
    return "\\\\n".join(lines)

def main(args):
    url: str = args.get('url', False)
    if not url:
        return {"statusCode": 400}
    pdf = url.endswith('.pdf')
    txt = url.endswith('.txt')
    md: str = ""
    if pdf:
        print('downloading pdf')
        try:
            response = requests.get(url)
            with open('temp.pdf', 'wb') as f:
                f.write(response.content)
            text = extract_text('temp.pdf')
            md = convert_to_markdown(text)
        except:
            print("Error")
    elif txt:
        try:
            response = requests.get(url)
            text = response.text
            md = convert_to_markdown(text)
        except:
            print("error")
    return {'statusCode': 200, "body": md}