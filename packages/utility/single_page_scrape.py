#--web true
#--kind python:default
#--annotation description "Use this action to get the context of a single page"
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/utility/single_page_scrape

import requests
from bs4 import BeautifulSoup
import lxml
from bs4.element import Tag

blocks = ["p", "h1", "h2", "h3", "h4", "h5", "blockquote"]

def _extract_blocks(parent_tag) -> list:
    extracted_blocks = []
    for tag in parent_tag:
        if tag.name in blocks:
            extracted_blocks.append(tag)
            continue
        if isinstance(tag, Tag):
            if len(tag.contents) > 0:
                inner_blocks = _extract_blocks(tag)
                if len(inner_blocks) > 0:
                    extracted_blocks.extend(inner_blocks)
    return extracted_blocks

def to_plaintext(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "lxml")
    extracted_blocks = _extract_blocks(soup.body)
    extracted_blocks_texts = [block.get_text().strip() for block in extracted_blocks]
    return "\n".join(extracted_blocks_texts)

def main(args):
    url = args.get('url', None)
    if url == None:
        return {'statusCode': 400, 'body': 'you must provide an url'}
    response = requests.get(url)
    plain_text = to_plaintext(response.text)
    return {'statusCode': 200, 'body': plain_text}
    
