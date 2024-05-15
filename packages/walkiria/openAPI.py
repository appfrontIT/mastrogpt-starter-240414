#--web false
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "create and upload the target openAPI spec for the given action"
#--param JWT_SECRET $JWT_SECRET
#--param CONNECTION_STRING $CONNECTION_STRING
#--timeout 300000

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

def main(args):
    global AI
    global JWT
    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    token = args.get('token', False)
    action = args.get('action', False)
    if not token or not action:
        return {"statusCode": 400}
    connection_string = args.get('CONNECTION_STRING', False)
    if not connection_string:
        return{'statusCode': 500}
    client = MongoClient(connection_string)
    COLLECTION = client['mastrogpt']['users']
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(token, key=secret, algorithms='HS256')
    action_split = action.split("\n")
    path = action_split[0].split('web')[1]
    function = action.split('function:')[1]
    messages = [
        {"role": "system", "content": "Given an action, you must produce the correct openAPI spec. An action is an API endpoint. Answer without code block"},
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
    data = COLLECTION.find_one({'_id': ObjectId(JWT['id'])}, {'yaml': 1, '_id': 0})
    yaml = data['yaml']
    yaml += f'\n{content}'
    upload = requests.post('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/add', headers={'Authorization': f"Bearer {token}"}, json={
        'text': yaml,
        'target': "default.yaml",
    })
    if upload.status_code == 204:
        COLLECTION.update_one({'_id': ObjectId(JWT['id'])}, {"$set": {'yaml': yaml}})
    return {'statusCode': 204}
