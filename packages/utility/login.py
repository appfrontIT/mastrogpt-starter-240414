#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY

import requests
import hashlib
from secrets import token_urlsafe

def main(args):
    username = args.get('username', False)
    password = args.get('password', False)
    if not username or not password:
        return {"statusCode": 400}
    user = requests.get(
        f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?username={username}&password={hashlib.sha256(password.encode()).hexdigest()}"
        )
    if user.status_code != 404 and user.status_code != 400:
        cookie = token_urlsafe(64)
        user_obj = user.json()
        update = requests.put('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/update?id=' + user_obj['_id'], json={
                "data": {"cookie": cookie}
                })
        return {
            "body": {"statusCode": 204},
            "headers": {'Set-Cookie': f'UserID={cookie}; Max-Age=43600; Version=; Path=/'},
            }
    return {"statusCode": user.status_code}