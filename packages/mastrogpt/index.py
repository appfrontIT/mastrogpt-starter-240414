#--web true
import json

def main(arg):
    data = {
        "services": [
            {
                "name": "Lookinglass",
                "url": "openai/chat"
            },
        ]
    }
    return {"body": data}

