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
                "name": "Coder",
                "url": "openai/coder"
            }
        ]
    }
    return {"body": data}

