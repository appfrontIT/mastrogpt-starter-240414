#--web true
import json

def main(arg):
    data = {
        "services": [
            {
                "name": "Lookinglass",
                "url": "lookinglass/chat"
            },
            {
                "name": "Coder",
                "url": "walkiria/coder_caller"
            },
            {
                "name": "Admin",
                "url": "admin/admin"
            },
            {
                "name": "Logout",
                "url": "utility/logout"
            }
        ]
    }
    return {"body": data}

