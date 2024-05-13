#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param JWT_SECRET $JWT_SECRET

import jwt
import requests
import hashlib
from secrets import token_urlsafe

SECRET = None

def token(cookie):
    if not cookie:
        return {"statusCode": 404, "body": "cookie not found"}
    split_cookie = cookie.split('=')
    user = requests.get(
        f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?cookie={split_cookie[1]}"
        )
    if user.status_code == 404:
        return {'statusCode': 404, 'body': 'user not found'}
    obj = user.json()
    encoded_jwt = jwt.encode({'id': str(obj['_id']), 'role': obj['role']}, SECRET, algorithm='HS256')
    return {
        "statusCode": 200,
        "body": {'token': encoded_jwt},
        }


def logout(args):
    cookie = args['__ow_headers'].get('cookie', False)
    if cookie:
        cookie_spl = cookie.split('=')
        user = requests.get(f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?cookie={cookie_spl[1]}")
        if user.status_code != 404:
            user_obj = user.json()
            update = requests.put('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/update?id='+user_obj['_id'], json={
                    "data": {"cookie": None}
            })
    return {
        "statusCode": 200,
        "headers": {'Set-Cookie': 'appfront-sess-cookie=;expires=Thu, 01 Jan 1970 00:00:01 GMT'}
        }

def login(args):
    username = args.get('username', False)
    password = args.get('password', False)
    if not username or not password:
        return {"statusCode": 400}
    user = requests.get(
        f"https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/find_one?username={username}&password={hashlib.sha256(password.encode()).hexdigest()}"
        )
    if user.status_code != 404 and user.status_code != 400:
        cookie = token_urlsafe(64)
        obj = user.json()
        encoded_jwt = jwt.encode({'id': str(obj['_id']), 'role': obj['role']}, SECRET, algorithm='HS256')
        update = requests.put('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/users/update?id=' + obj['_id'], json={
                "data": {"cookie": cookie}
                })
        return {
            "statusCode": 200,
            "body": {'token': encoded_jwt},
            "headers": {'Set-Cookie': f'appfront-sess-cookie={cookie}; Max-Age=43600; Version=; Path=/'},
            }
    return {"statusCode": user.status_code}

def main(args):
    global SECRET
    SECRET = args.get('JWT_SECRET')
    path = args.get('__ow_path', False)
    if path == '/login' and args['__ow_method'] == 'post':
        return login(args)
    if path == '/logout' and args['__ow_method'] == 'delete':
        return logout(args)
    if path == '/token' and args['__ow_method'] == 'get':
        headers = args['__ow_headers']
        return token(headers.get('cookie', False))
    return {"statusCode": 404}