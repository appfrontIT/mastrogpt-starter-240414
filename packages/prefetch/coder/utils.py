from bs4 import BeautifulSoup
import requests
import os
import requests
from requests.auth import HTTPBasicAuth
import json
from zipfile import ZipFile 

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

def delete_action(package, name):
    resp = requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return resp.text

def action_info(package, name):
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return resp.text

def get_actions():
    resp = requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(OW_API_SPLIT[0], OW_API_SPLIT[1]))
    return resp.text

def crawl(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching page")
        return ""
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

def load_zip(path):
    name = path.split('.zip')[0]
    with ZipFile(path, 'r') as myzip:
        file_list = myzip.namelist()
        for file in file_list:
            content = str(myzip.read(file))
            requests.post('https://nuvolaris.dev/api/v1/web/gporchia/embedding/embed', json={"name": name, "data": content})