from bs4 import BeautifulSoup
import requests
import os
import requests
from requests.auth import HTTPBasicAuth
import json

OW_KEY = os.getenv('__OW_API_KEY')

def delete_action(name):
    split = OW_KEY.split(':')
    if name[0] == '/':
        name = name[:1]
    resp = requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}", auth=HTTPBasicAuth(split[0], split[1]))
    return resp.text

def action_info(name):
    split = OW_KEY.split(':')
    if name[0] == '/':
        name = name[:1]
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}", auth=HTTPBasicAuth(split[0], split[1]))
    return resp.text

def get_actions():
    split = OW_KEY.split(':')
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(split[0], split[1]))
    return resp.text

def crawl(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching page")
        return ""
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
