from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
import requests
import re
import os
import config
import json

MAN_ROLE="""
You only answer to the informations found at https://appfront-operations.gitbook.io/lookinglass-manuale-utente.
"""

