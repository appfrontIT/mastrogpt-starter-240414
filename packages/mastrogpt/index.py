#--web true
import json

def main(arg):
    data = {
        "services": [
            {
                "name": "Lookinglass",
                "url": "openai/chat"
            },
            {
                "name": "OpenAI",
                "url": "openai/gpt"
            }
        ]
    }
    return {"body": data}

