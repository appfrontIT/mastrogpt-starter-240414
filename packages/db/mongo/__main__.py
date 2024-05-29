#--web raw
#--kind python:default
#--annotation description "an action which perform operations to the database, suche as: add, update, delete, find. Required parameters: {'db': db name, 'collection': collection name, 'type of operation(add, find_one, find, delete, update)': True, 'data': required data as json. Example: 'name': name, 'role': role, 'password': password, ...}"
#--param CONNECTION_STRING $CONNECTION_STRING

from pymongo import MongoClient, errors
from pymongo.collection import Collection
import json
from bson.objectid import ObjectId
import base64

def update(collection: Collection, data, id = False):
    if not id or not data:
        return {"statusCode": 400, "body": "error: parameter 'id' missing or 'data' missing"}
    split = id.split('=')
    if len(split) == 2:
        if split[0] == 'id':
            id = split[1]
    if not id:
        return {"statusCode": 400, "body": "error: parameter 'id'"}
    response = collection.update_one({'_id':ObjectId(id)}, {"$set": json.loads(data)['data']})
    if response.modified_count == 0:
        return {"statusCode": 404}
    el = collection.find_one({'_id': ObjectId(id)})
    el['_id'] = str(el['_id'])
    return {"statusCode": 200, "body": el}

def delete(collection, id = False):
    if not id:
        return {"statusCode": 400, "body": "error: parameter 'id' missing"}
    split = id.split('=')
    if len(split) == 2:
        if split[0] == 'id':
            id = split[1]
    data = collection.delete_one({'_id':ObjectId(id)})
    if data.deleted_count == 1:
        return {"statusCode": 204}
    return {"statusCode": 404}

def find_one(collection: Collection, query_param):
    n_params = query_param.split('&')
    filter = {}
    for param in n_params:
        split_params = param.split('=')
        if split_params[0] == 'id':
            filter['_id'] = ObjectId(split_params[1])
        else:
            filter[split_params[0]] = split_params[1]
    data = collection.find_one(filter)
    if data:
        data['_id'] = str(data['_id'])
        return {"statusCode": 200, "body": data}
    return {"statusCode": 404}

def find_many(collection: Collection, query_param = False):
    filter = {}
    if query_param:
        n_params = query_param.split('&')
        for param in n_params:
            split_params = param.split('=')
            filter[split_params[0]] = split_params[1]
    data = collection.find(filter)
    ret = []
    for x in data:
        x['_id'] = str(x['_id'])
        ret.append(x)
    if len(ret) > 0:
        return {"statusCode": 200, "body": ret}
    return {"statusCode": 404}

def add(collection: Collection, data = False):
    if not data:
        return {"statusCode": 400, "body": "parameter 'data' is missing"}
    ins = collection.insert_one(json.loads(data)['data'])
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

def main(args):
    token = args['__ow_headers'].get('authorization', False)
    # if not token:
    #     return {'statusCode': 401}
    token = token.split(' ')
    if len(token) != 2 and token[0] != 'Bearer':
        return {'statusCode': 401}
    token = token[1]
    connection_string = args.get('CONNECTION_STRING', False)
    path: str = args.get('__ow_path', False)
    path_spl = path[1:].split('/')
    if len(path_spl) != 3:
        return {"statusCode": 400}
    db = path_spl[0]
    collection = path_spl[1]
    if not collection or not db:
        return {"statusCode": 400, "body": "parameter 'db' or 'collection' missing"}
    
    client = MongoClient(connection_string)
    dbname = client[db]

    collection_list = dbname.list_collection_names()
    db_coll = ""
    if collection in collection_list:
        db_coll = dbname[collection]
    else:
        db_coll = dbname.create_collection(collection)
    
    op = path_spl[2]
    method = args['__ow_method']
    if op == 'find_one' and method == 'get':
        return find_one(db_coll, args['__ow_query'])
    elif op == 'find_many' and method == 'get':
        return find_many(db_coll, args['__ow_query'])
    elif op == 'add' and method == 'post':
        try:
            body: str = args['__ow_body']
            decoded = base64.b64decode(body).decode('utf-8')
        except:
            return {"body": "Could not decode body from Base64."}
        return add(collection=db_coll, data=decoded)
    elif op == 'add_many' and method == 'post':
            return add_many(db_coll, args.get('data', False))
    elif op == 'delete' and method == 'delete':
        return delete(db_coll, args['__ow_query'])
    elif op == 'update' and method == 'put':
        try:
            body: str = args['__ow_body']
            decoded = base64.b64decode(body).decode('utf-8')
        except:
            return {"body": "Could not decode body from Base64."}
        return update(db_coll, decoded, args['__ow_query'])
    return {"statusCode": 400}