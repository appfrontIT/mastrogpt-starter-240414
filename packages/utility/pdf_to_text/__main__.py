#--web true
#--kind python:default
#--annotation description "This action extracts data from an image and return the data"
#--timeout 300000
#--param OPENAI_API_KEY $OPENAI_API_KEY
#--annotation url https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/utility/carta_circ_to_data

import requests
import convertapi
from os.path import isfile, join
from os import listdir
from os import mkdir
import os

def main(args):
    name: str = args.get('name', None)
    url: str = args.get('url', None)
    if not name and not url:
        return {"statusCode": 400, "body": "bad request: you must provide name or url"}
    convertapi.api_secret = '9vI2gUCIJLtUyTSi'
    if url:
        paths = url.split('/')
        filename = paths[-1]
        extension = filename.split('.')[-1]
        result = convertapi.convert('txt', { 'File': url }, from_format = extension)
        ret = []
        for file in result.files:
            r = requests.get(file.url)
            r.encoding = r.apparent_encoding
            ret.append(r.text)
        return {"statusCode": 200, "body": ret}
    elif name:
        paths = name.split('/')
        filename = paths[-1]
        extension = filename.split('.')[-1]
        response = requests.get(f'https://walkiria.cloud/api/v1/web/{os.environ['__OW_NAMESPACE']}/db/minio/static/find?name=' + name)
        if response.ok:
            obj = response.json()
            data = obj['data']
    if not data or not extension:
        return {"statusCode": 404, "body": "there was an error retrieving the data"}
    return {"statusCode": 404}
        