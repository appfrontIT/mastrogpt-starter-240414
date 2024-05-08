#--web true
#--kind python:default
#--annotation description "This action convert a pdf into a markdown string"
#--timeout 300000

import requests
from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def convert_to_markdown(text):
    lines = text.split("\\\\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.isupper() and len(stripped) < 50:
            lines[i] = f"## {stripped}"
    return "\\\\n".join(lines)

def main(args):
    pdf = args.get('pdf', False)
    txt = args.get('text', False)
    if not pdf and not txt:
        return {"statusCode": 400}
    if pdf:
        try:
            response = requests.get(pdf)
        except:
            print("Error")
        text = extract_text_from_pdf(response.content)
        md = convert_to_markdown(text)
    elif txt:
        try:
            response = requests.get(txt)
        except:
            print("error")
        text = response.text
        md = convert_to_markdown(text)
    return {"body": md}