#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY

import requests
import hashlib
from secrets import token_urlsafe

def main(args):
    name = args.get('user', False)
    password = args.get('password', False)
    if not name or not password:
        return {"statusCode": 400}
    data = {
        "find_one": True,
        "filter": {
            "name": name,
            "password": hashlib.sha256(password.encode()).hexdigest(),
        }
    }
    user = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/db/mongo", json={"find_one": True, "collection": "users", "data": data})
    if user.status_code != 404:
        cookie = token_urlsafe(64)
        user_obj = user.json()
        update = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo', json={
            "update": True,
            "collection": "users",
            "data": {
                "filter": {"_id": user_obj['ID']},
                "updateData": {"cookie": cookie}
            }
        })
        return {
            "body": {"statusCode": 200},
            "headers": {'Set-Cookie': f'UserID={cookie}; Max-Age=43600; Version=; Path=/'},
            }
    return {"statusCode": user.status_code}