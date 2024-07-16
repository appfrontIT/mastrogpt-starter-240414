#--web true
#--kind python:default
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation description "This action returns all mongo collections inside the passed database"
#--annotation url https://walkiria.cloud/api/v1/web/mcipolla/db/get_coll_list

from pymongo import MongoClient
import json
import os

def main(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    connection_string = args.get('CONNECTION_STRING', False)
    client = MongoClient(connection_string)
    dbname = client['mcipolla']
    collection_list = dbname.list_collection_names()
    crawled_pages = []
    for col in collection_list:
        if 'crawl' in col:
            collection = dbname[col]
            cursor = collection.find({})
            coll_els = []
            for item in cursor:
                obj = {}
                for el in item:
                    if el != '_id':
                        obj[el] = item[el]
                coll_els.append(obj)
            crawled_pages.append({'domain': col, 'data': coll_els})
    return {'statusCode': 200, 'body': crawled_pages}