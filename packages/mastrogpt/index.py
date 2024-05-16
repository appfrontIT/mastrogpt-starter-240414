#--web true
import json

def main(arg):
    data = {
        "services": [
            {
                "name": "Lookinglass",
                "url": "default/invoke/lookinglass"
            },
            {
                "name": "Coder",
                "url": "default/invoke/walkiria"
            },
            {
                "name": "Admin",
                "url": "default/invoke/admin"
            },
            {
                "name": "Tester",
                "url": "default/invoke/test"
            },
            {
                "name": "Logout",
                "url": "default/auth/logout"
            }
        ]
    }
    return {"body": data}

