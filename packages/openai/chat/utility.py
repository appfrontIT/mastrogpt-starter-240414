from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
import requests
import re
import os
import config
import json

def htm_to_text(url):
    req = requests.get(url)
    raw_text = req.text
    print(raw_text)
    