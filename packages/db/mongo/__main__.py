#--web true
#--kind python:default
#--annotation description "an action which perform operations to the database, suche as: add, update, delete, find. Required parameters: {'db': db name, 'collection': collection name, 'type of operation(add, find_one, find, delete, update)': True, 'data': required data as json. Example: 'name': name, 'role': role, 'password': password, ...}"

from pymongo import MongoClient
import json
from bson.objectid import ObjectId

def format_el(element):
    ret = {}
    for key in element:
        if key == '_id':
            id = element[key]
            ret['ID'] = str(id)
        else:
            ret[key] = element[key]
    return json.dumps(ret)

def update(collection, filter, update_data):
    to_update = {}
    for key in update_data:
        if update_data[key] != "":
            to_update[key] = update_data[key]
    data = collection.update_one({'_id':ObjectId(filter['_id'])}, {"$set": to_update})
    el = collection.find_one({'_id': ObjectId(filter['_id'])})
    return {"body": format_el(el)}

def delete(collection, filter):
    print(filter)
    el = collection.find_one({'_id': ObjectId(filter['_id'])})
    deleted_el = format_el(el)
    data = collection.delete_one({'_id':ObjectId(filter['_id'])})
    return {"body": deleted_el}

def find(collection, filter):
    to_filter = {}
    for key in filter:
        if filter[key] != "":
            to_filter[key] = filter[key]
    data = collection.find(to_filter)
    ret = []
    for x in data:
        ret.append(format_el(x))
    return {"body": json.dumps(ret)}

def find_one(collection, filter):
    to_filter = {}
    for key in filter:
        if filter[key] != "":
            to_filter[key] = filter[key]
    data = collection.find_one(to_filter)
    if data:
        return {"body": format_el(data)}
    return {"body": json.dumps(data)}

def main(args):
    # connection_string = args.get('CONNECTION_STRING')
    db = args.get('db', '')
    if db == '':
        db = 'mastrogpt'
    collection = args.get('collection', '')
    data = args.get('data', '')
    if collection == '':
        return {"body": "error, collection missing"}
    if data == '':
        return {"body": "error, data is missing"}
    
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client[db]
    
    collection_list = dbname.list_collection_names()
    db_coll = ""
    if collection in collection_list:
        db_coll = dbname[collection]
    else:
        db_coll = dbname.create_collection(collection)
    
    if args.get('add'):
        ins = db_coll.insert_one(data).inserted_id
        el = db_coll.find_one({'_id': ins})
        return {"body": format_el(el)}
    elif args.get('find_one') == True:
        return find_one(db_coll, data.get('filter', ''))
    elif args.get('find') == True:
        return find(db_coll, data.get('filter', ''))
    elif args.get('delete') == True:
        return delete(db_coll, data.get('filter', ''))
    elif args.get('update') == True:
        return update(db_coll, data.get('filter', ''), data.get('updateData', ''))
    return {"body": "error couldn't find any method(add, find_one, find, delete, update)"}