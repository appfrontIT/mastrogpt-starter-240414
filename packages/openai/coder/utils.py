from bs4 import BeautifulSoup
import requests
import os
import requests
from requests.auth import HTTPBasicAuth
import json

def action_info(name):
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{name}", auth=HTTPBasicAuth(split[0], split[1]))
    print(resp.text)

def get_actions():
    ow_key = os.getenv('__OW_API_KEY')
    split = ow_key.split(':')
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(split[0], split[1]))
    # print(resp.text)
    obj = json.loads(resp.text)
    name_arr = []
    for x in obj:
        name_arr.append(x['name'])
    # print(name_arr)
    return name_arr

def crawl(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching page")
        return ""
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()