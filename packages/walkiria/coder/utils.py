from bs4 import BeautifulSoup
import requests
import os
import requests
from requests.auth import HTTPBasicAuth
import json
from zipfile import ZipFile
import config

def delete_action(package, name):
    return requests.delete(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1])).text

def action_info(package, name):
    return requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions/{package}/{name}", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1])).text

def get_actions():
    return requests.get(f"https://nuvolaris.dev/api/v1/namespaces/gporchia/actions", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1])).text

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