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
                "url": "openai/coder_caller"
            },
            {
                "name": "Admin",
                "url": "openai/admin"
            }
        ]
    }
    return {"body": data}

