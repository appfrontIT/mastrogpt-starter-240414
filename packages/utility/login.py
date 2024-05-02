#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

import requests
from secrets import token_urlsafe

def main(args):
    user = requests.post("https://nuvolaris.dev/api/v1/web/gporchia/user/find_user", headers={"Content-Type": "application/json"}, json={
        "name": args.get('user', ''),
        "password": args.get('password', '')
        })
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
    return {"statusCode": 400}