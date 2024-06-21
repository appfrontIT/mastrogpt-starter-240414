#--web true
#--kind python:default
#--memory 512
#--param CONNECTION_STRING $CONNECTION_STRING
#--annotation description "an action which perform operations to the database, suche as: add, update, delete, find. Required parameters: {'db': db name, 'collection': collection name, 'type of operation(add, find_one, find, delete, update)': True, 'data': required data as json. Example: 'name': name, 'role': role, 'password': password, ...}"
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/db/mongo

from pymongo import MongoClient, errors
from pymongo.collection import Collection
import json
from bson.objectid import ObjectId
import base64
import pandas as pd
from urllib.parse import unquote

def csv_to_json(filename, header=None):
    filename = filename.replace(';', ',')
    split = filename.split('\n')
    keys = split[0].split(',')
    ret = []
    for lines in split[1:]:
        vals = lines.split(',')
        obj = {}
        if len(vals) != len(keys):
            continue
        for i in range(len(vals)):
            obj[keys[i]] = vals[i]
        ret.append(obj)
    return ret

def update(collection: Collection, data, id = False):
    if not id or not data:
        return {"statusCode": 400, "body": "error: parameter 'id' missing or 'data' missing"}
    if not id:
        return {"statusCode": 400, "body": "error: parameter 'id'"}
    response = collection.update_one({'_id':ObjectId(id)}, {"$set": data})
    if response.modified_count == 0:
        return {"statusCode": 404}
    el = collection.find_one({'_id': ObjectId(id)})
    el['_id'] = str(el['_id'])
    return {"statusCode": 200, "body": el}

def delete(collection, id = False):
    if not id:
        return {"statusCode": 400, "body": "error: parameter 'id' missing"}
    data = collection.delete_one({'_id':ObjectId(id)})
    if data.deleted_count == 1:
        return {"statusCode": 204}
    return {"statusCode": 404}

def find_one(collection: Collection, args):
    filter = args.get('filter', {})
    if filter != {}:
        filter = json.loads(unquote(filter))
    fields = args.get('fields', {})
    if fields != {}:
        fields = json.loads(unquote(fields))
    data = collection.find_one(filter, fields)
    if data:
        data['_id'] = str(data['_id'])
        return {"statusCode": 200, "body": data}
    return {"statusCode": 404}

def find_many(collection: Collection, args):
    filter = args.get('filter', {})
    fields = args.get('fields', {})
    if filter != {}:
        filter = json.loads(unquote(filter))
    fields = args.get('fields', {})
    if fields != {}:
        fields = json.loads(unquote(fields))
    n_result = args.get('n_results', -1)
    if n_result != -1:
        data = collection.find(filter, fields).limit(int(n_result))
    else:    
        data = collection.find(filter, fields)
    ret = []
    for x in data:
        if '_id' in x:
            x['_id'] = str(x['_id'])
        ret.append(x)
    return {"statusCode": 200, "body": ret}

def add(collection: Collection, data = False):
    if not data:
        return {"statusCode": 400, "body": "parameter 'data' is missing"}
    ins = collection.insert_one(data)
    if not ins.acknowledged:
        return {"statusCode": 400}
    el = collection.find_one({'_id': ins.inserted_id})
    el['_id'] = str(el['_id'])
    return {"body": el, "statusCode": 200}

def add_many(collection: Collection, data):
    if not data:
        return {"statusCode": 400, "body": "error: 'data'"}
    try:
        ins = collection.insert_many(data)
        if not ins.acknowledged:
            return {"statusCode": 400}
        return {"statusCode": 204}
    except errors.OperationFailure as exc:
        return {"statusCode": 404, "body": f"{exc.code}: {exc.details}"}
    
def add_csv(collection: Collection, data = False):
    if not data:
        return {"statusCode": 400, "body": "parameter 'data' is missing"}
    try:
        csv_data = csv_to_json(data, header=0)
        ins = collection.insert_many(csv_data)
        if not ins.acknowledged:
            return {"statusCode": 400}
        return {"statusCode": 204}
    except errors.OperationFailure as exc:
        return {"statusCode": 404, "body": f"{exc.code}: {exc.details}"}

def main(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')
    if len(token) != 2 and token[0] != 'Bearer':
        return {'statusCode': 401}
    token = token[1]
    connection_string = args.get('CONNECTION_STRING', False)
    path: str = args.get('__ow_path', False)
    path_spl = path[1:].split('/')
    db = path_spl[0]
    collection = path_spl[1]
    if not collection or not db:
        return {"statusCode": 400, "body": "parameter 'db' or 'collection' missing"}
    client = MongoClient(connection_string)
    dbname = client[db]

    collection_list = dbname.list_collection_names()
    method = args['__ow_method']
    if collection == 'get_collections' and method == 'get':
        return {"statusCode": 200, "body": collection_list}
    db_coll = ""
    if collection in collection_list:
        db_coll = dbname[collection]
    else:
        db_coll = dbname.create_collection(collection)
    
    if len(path_spl) != 3:
        return {"statusCode": 400}
    op = path_spl[2]
    if op == 'find_one' and method == 'get':
        return find_one(db_coll, args)
    elif op == 'find_many' and method == 'get':
        return find_many(db_coll, args)
    elif op == 'add' and method == 'post':
        return add(collection=db_coll, data=args.get('data', None))
    elif op == 'add_many' and method == 'post':
            return add_many(db_coll, args.get('data', None))
    elif op == 'add_csv' and method == 'post':
        return add_csv(collection=db_coll, data=args.get('data', None))
    elif op == 'delete' and method == 'delete':
        return delete(db_coll, args)
    elif op == 'update' and method == 'put':
        return update(db_coll, args.get('data', None), args)
    return {"statusCode": 400}