import os

html = ""
editor = ""
session_user = None

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
QUERY: str = ""
# AI: OpenAI = None