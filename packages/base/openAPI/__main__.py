#--web true
#--kind python:default
#--annotation provide-api-key true
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation description "create and upload the target openAPI spec for the given action"
#--param JWT_SECRET $JWT_SECRET
#--timeout 300000
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/base/openAPI

from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from pymongo.collection import Collection
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import jwt
from openai import OpenAI

AI: OpenAI = None
JWT = None

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

def add(path, function, openapi, COLLECTION):
    messages = [
        {"role": "system", "content": """Given an action, you must produce the correct openAPI spec. An action is an API endpoint. If the action needs authorization, you must specify it.
        Answer only with the spec starting from the path. Nothing else must be returned. The output must be in JSON format. Example:
          {
            "/gporchia/pippo/multiply_by_4": {
            "post": {
              "tags": [
                "pippo"
              ],
              "summary": "Multiply given number by 4",
              "description": "This API multiplies the given number by 4.",
              "operationId": "multiply_by_4",
              "requestBody": {
                "required": true,
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "number": {
                          "type": "number",
                          "description": "The number to be multiplied by 4",
                          "example": 5
                        }
                      },
                      "required": [
                        "number"
                      ]
                    }
                  }
                }
              },
              "responses": {
                "200": {
                  "description": "successful operation",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "result": {
                            "type": "number",
                            "description": "The result of the multiplication"
                          }
                        }
                      }
                    }
                  }
                },
                "400": {
                  "description": "Invalid input",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "error": {
                            "type": "string",
                            "description": "Error message"
                          }
                        }
                      }
                    }
                  }
                },
                "500": {
                  "description": "Server error",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "error": {
                            "type": "string",
                            "description": "Error message"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """},
        {"role": "user", "content": f"""the openAPI path is: {path}. The function to insert is {function}\n"""}
    ]
    response = AI.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={ "type": "json_object" }
    )
    content = response.choices[0].message.content
    openapi = openapi[:-3]
    if openapi[len(openapi) - 2] == '}':
        openapi = openapi[:-1]
        openapi += ',\n'
    openapi += f'{content[1:]}\n' + '}'
    if not validateJSON(openapi):
        validate_json = AI.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "your job is to validate the correctness of an openapi json, and return the correct json. Only the openapi json must be returned, nothing else"},
            {"role": "user", "content": "please, check and correct the following openapi spec:\n" + openapi }
        ],
        response_format={ "type": "json_object" }
        )
        openapi = validate_json.choices[0].message.content
    COLLECTION.update_one({'_id': ObjectId(JWT['id'])}, {"$set": {'openapi': openapi}})
    return {'statusCode': 200, 'body': openapi}

def delete(path, openapi, COLLECTION, token):
    start = openapi.find(path)
    end = openapi.find('\n\n', start)
    if end == -1:
        openapi = openapi.replace(openapi[start:], '')
    else:
        openapi = openapi.replace(openapi[start:end + 2], '')
    if not validateJSON(openapi):
        validate_json = AI.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "your job is to validate the correctness of an openapi json, and return the correct json. Only the openapi json must be returned, nothing else"},
            {"role": "user", "content": "please, check and correct the following openapi spec:\n" + openapi }
        ],
        response_format={ "type": "json_object" }
        )
        openapi = validate_json.choices[0].message.content
    COLLECTION.update_one({'_id': ObjectId(JWT['id'])}, {"$set": {'openapi': openapi}})
    return {'statusCode': 204}

def main(args):
    global AI
    global JWT

    AI = OpenAI(api_key=args['OPENAI_API_KEY'])
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {"statusCode": 401}
    token = token.split(' ')[1]
    connection_string = "mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0"
    if not connection_string:
        return{'statusCode': 500}
    client = MongoClient(connection_string)
    COLLECTION = client['mastrogpt']['users']
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(token, key=secret, algorithms='HS256')
    data = COLLECTION.find_one({'_id': ObjectId(JWT['id'])}, {'openapi': 1, '_id': 0})
    openapi = data['openapi']
    path = args.get('__ow_path', False)
    if path == '/add' and (args['__ow_method'] == 'post' or args['__ow_method'] == 'put'):
        action = args.get('action', False)
        if not action:
            return {"statusCode": 401}
        function = action.split('function:')[1]
        action_split = action.split("\n")
        action_path = action_split[0].split('web')[1]
        return add(action_path, function, openapi, COLLECTION)
    elif path == '/delete' and args['__ow_method'] == 'delete':
        action = args.get('action', False)
        if not action:
            return {"statusCode": 404, "body": "'action' key not found"}
        return delete(action, openapi, COLLECTION, token)
    elif path == '/get' and args['__ow_method'] == 'get':
        return {'statusCode': 200, 'body': openapi}
    return {'statusCode': 404}