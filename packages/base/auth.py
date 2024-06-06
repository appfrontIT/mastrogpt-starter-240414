#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--param JWT_SECRET $JWT_SECRET
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/base/auth

import jwt
import requests
import hashlib
from secrets import token_urlsafe
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from pymongo.collection import Collection
import json

SECRET = None
COLLECTION = None

def get_user(cookie):
    split_cookie = cookie.split('=')
    user = COLLECTION.find_one({'cookie': split_cookie[1]})
    if user:
        user['_id'] = str(user['_id'])
        return {'statusCode': 200, 'body': user}
    return {'statusCode': 404, 'body': 'user not found'}

def token(cookie):
    if not cookie:
        return {"statusCode": 404, "body": "cookie not found"}
    split_cookie = cookie.split('=')
    user = COLLECTION.find_one({'cookie': split_cookie[1]})
    if not user:
        return {'statusCode': 404, 'body': 'user not found'}
    encoded_jwt = jwt.encode({
            'id': str(user['_id']),
            'username': user['username'],
            'role': user['role'],
            'package': user['package'],
            'namespace': user['namespace'],
            'shared_package': user['shared_package'],
            },
            SECRET, algorithm='HS256')
    COLLECTION.update_one({'_id': user['_id']}, {"$set": {'JWT': encoded_jwt}})
    return {
        "statusCode": 200,
        "body": {'token': encoded_jwt},
        }

def logout(args):
    cookie = args['__ow_headers'].get('cookie', False)
    if cookie:
        cookie_spl = cookie.split('=')
        COLLECTION.update_one({'cookie': cookie_spl[1]}, {"$set": {'JWT': None, 'cookie': None}})
    return {
        "statusCode": 200,
        "headers": {'Set-Cookie': 'appfront-sess-cookie=;expires=Thu, 01 Jan 1970 00:00:01 GMT'}
        }

def login(args):
    username = args.get('username', False)
    password = args.get('password', False)
    if not username or not password:
        return {"statusCode": 400}
    user = COLLECTION.find_one({'username': username, 'password': hashlib.sha256(password.encode()).hexdigest()})
    if user:
        cookie = token_urlsafe(64)
        encoded_jwt = jwt.encode({
            'id': str(user['_id']),
            'role': user['role'],
            'package': user['package'],
            'namespace': user['namespace'],
            'shared_package': user['shared_package'],
            },
            SECRET, algorithm='HS256')
        COLLECTION.update_one({'_id': user['_id']}, {"$set": {'JWT': encoded_jwt, 'cookie': cookie}})
        return {
            "statusCode": 200,
            "body": {'token': encoded_jwt},
            "headers": {'Set-Cookie': f'appfront-sess-cookie={cookie}; Max-Age=43600; Version=; Path=/'},
            }
    return {"statusCode": user.status_code}

def main(args):
    global SECRET
    global COLLECTION
    SECRET = args.get('JWT_SECRET')
    connection_string = args.get('CONNECTION_STRING', False)
    if not connection_string:
        return{'statusCode': 500}
    client = MongoClient(connection_string)
    COLLECTION = client['mastrogpt']['users']
    path = args.get('__ow_path', False)
    if path == '/login' and args['__ow_method'] == 'post':
        return login(args)
    if path == '/logout' and args['__ow_method'] == 'delete':
        return logout(args)
    if path == '/token' and args['__ow_method'] == 'get':
        headers = args['__ow_headers']
        cookie = headers.get('cookie', False)
        if not cookie:
            return {'statusCode': 404}
        return token(cookie)
    if path == '/user' and args['__ow_method'] == 'get':
        headers = args['__ow_headers']
        cookie = headers.get('cookie', False)
        if not cookie:
            return {'statusCode': 404}
        return get_user(cookie)
    return {"statusCode": 404}