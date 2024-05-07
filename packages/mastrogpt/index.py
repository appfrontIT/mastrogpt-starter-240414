#--web true
import json

def main(arg):
    data = {
        "services": [
            {
                "name": "Lookinglass",
                "url": "openai/lookinglass"
            },
            {
                "name": "Coder",
                "url": "openai/coder_caller"
            },
            {
                "name": "Admin",
                "url": "openai/admin"
            },
            {
                "name": "Logout",
                "url": "mastrogpt/logout"
            }
        ]
    }
    return {"body": data}

