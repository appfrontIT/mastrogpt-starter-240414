from bs4 import BeautifulSoup
import requests
import os
import requests
from requests.auth import HTTPBasicAuth
import json
from zipfile import ZipFile
import config
import tiktoken

def delete_action(name, package):
    if package == 'default':
        return requests.delete(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/{name}", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]))    
    return requests.delete(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/{package}/{name}", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]))

def action_info(name, package = None):
    if package and package != 'default':
        return requests.get(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/{package}/{name}", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]))
    return requests.get(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions/{name}", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]))

def get_actions():
    return requests.get(f"https://walkiria.cloud/api/v1/namespaces/{os.environ['__OW_NAMESPACE']}/actions", auth=HTTPBasicAuth(config.OW_API_SPLIT[0], config.OW_API_SPLIT[1]))

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
            requests.post(f'https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/embedding/embed', json={"name": name, "data": content})

def num_tokens(text: str, model: str = 'gtp-4o') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))