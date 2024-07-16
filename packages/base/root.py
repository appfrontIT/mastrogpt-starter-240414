#--web false
#--kind python:default
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation provide-api-key true

from pymongo import MongoClient, errors
import secrets
import hashlib
from requests.auth import HTTPBasicAuth
import requests
import os

OW_KEY = os.getenv('__OW_API_KEY')
SPLIT = OW_KEY.split(':')

def main(args):
    connection_string = args.get('CONNECTION_STRING', False)
    client = MongoClient(connection_string)
    password = secrets.token_urlsafe(7)
    print(password)
    COLLECTION = client['mcipolla']['users']
    openapi = f"""{{
        "openapi": "3.1.0",
        "info": {{
            "title": "root - OpenAPI 3.1",
    "termsOfService": "http://swagger.io/terms/",
    "version": "1.0.11"
    }},
    "servers": [{{"url": "https://walkiria.cloud/api/v1/web"}}],
    "components": {{
    "securitySchemes": {{
        "bearerAuth": {{
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
            }}
        }}
    }},
    "paths": {{}}
    }}"""
    user = COLLECTION.insert_one({
        "name": '',
        "surname": '',
        "username": 'root',
        "mobile": "",
        "address": "",
        "postcode": "",
        "country": "",
        "state":  "",
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "email": '',
        "role": 'root',
        "active": True,
        "namespace": f"mcipolla/core",
        "package": 'core',
        "shared_package": [],
        "chat": [],
        "openapi": openapi,
        "teams": []
    })
    body = {
        "namespace": "mcipolla",
        "name": 'core',
        "publish": False
        }
    resp = requests.put(f"https://walkiria.cloud/api/v1/namespaces/mcipolla/packages/core",
                    auth=HTTPBasicAuth(SPLIT[0], SPLIT[1]),
                    headers={"Content-type": "application/json"},
                    json=body
                    )
    return {"statusCode": resp.status_code, 'body': resp.json()}