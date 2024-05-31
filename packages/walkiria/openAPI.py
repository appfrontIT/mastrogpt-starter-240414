#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "create and upload the target openAPI spec for the given action"
#--param JWT_SECRET $JWT_SECRET
#--param CONNECTION_STRING $CONNECTION_STRING
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/walkiria/openAPI

from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from pymongo.collection import Collection
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import jwt
from openai import OpenAI

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')
AI: OpenAI = None
JWT = None

def add(path, function, yaml, COLLECTION, token):
    messages = [
        {"role": "system", "content": "Given an action, you must produce the correct openAPI spec. An action is an API endpoint. If the action needs authorization, you must specify it. Answer only with the spec starting from the path. Nothing else must be returned"},
        {"role": "user", "content": f"""the openAPI path is: {path}. The function to insert is {function}\n"""}
    ]
    response = AI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    content = response.choices[0].message.content
    content = content.replace('```yaml', '')
    content = content.replace('```', '')
    content = content.replace('paths:\n', '')
    yaml += f'\n{content}'
    upload = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/add', headers={'Authorization': f"Bearer {token}"}, json={
        'text': yaml,
        'target': "default.yaml",
    })
    if upload.status_code == 204:
        COLLECTION.update_one({'_id': ObjectId(JWT['id'])}, {"$set": {'yaml': yaml}})
    return {'statusCode': upload.status_code}

def delete(path, yaml, COLLECTION, token):
    start = yaml.find(path)
    end = yaml.find('\n\n', start)
    if end == -1:
        yaml = yaml.replace(yaml[start:], '')
    else:
        yaml = yaml.replace(yaml[start:end + 2], '')
    upload = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/add', headers={'Authorization': f"Bearer {token}"}, json={
        'text': yaml,
        'target': "default.yaml",
    })
    if upload.status_code == 204:
        COLLECTION.update_one({'_id': ObjectId(JWT['id'])}, {"$set": {'yaml': yaml}})
    return {'statusCode': upload.status_code}

def main(args):
    global AI
    global JWT
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    token = args['__ow_headers'].get('authorization', False)
    action = args.get('action', False)
    if not token or not action:
        return {"statusCode": 401}
    token = token.split(' ')[1]
    connection_string = args.get('CONNECTION_STRING', False)
    if not connection_string:
        return{'statusCode': 500}
    client = MongoClient(connection_string)
    COLLECTION = client['mastrogpt']['users']
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(token, key=secret, algorithms='HS256')
    data = COLLECTION.find_one({'_id': ObjectId(JWT['id'])}, {'yaml': 1, '_id': 0})
    yaml = data['yaml']
    action_split = action.split("\n")
    action_path = action_split[0].split('web')[1]
    path = args.get('__ow_path', False)

    if path == '/add' and (args['__ow_method'] == 'post' or args['__ow_method'] == 'put'):
        function = action.split('function:')[1]
        return add(action_path, function, yaml, COLLECTION, token)
    elif path == '/delete' and args['__ow_method'] == 'delete':
        return delete(action_path, yaml, COLLECTION, token)
    return {'statusCode': 404}
