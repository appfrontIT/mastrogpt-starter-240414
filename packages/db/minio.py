#--web true
#--kind python:default
#--annotation description "an action which perform operations to Minio storage, suche as: add, update, delete, find. Required parameters: {'db': db name, 'collection': collection name, 'type of operation(add, find_one, find, delete, update)': True, 'data': required data as json. Example: 'name': name, 'role': role, 'password': password, ...}"
#--param MINIO_ACCESS_KEY $MINIO_ACCESS_KEY
#--param MINIO_SECRET_KEY $MINIO_SECRET_KEY
#--param MINIO_HOST $MINIO_HOST
#--param MINIO_PORT $MINIO_PORT
#--param JWT_SECRET $JWT_SECRET
#--annotation url https://nuvolaris.dev/api/v1/web/gporchia/db/minio

from datetime import timedelta
from xmlrpc.client import ResponseError
from minio import Minio
from minio.error import S3Error
import io
import jwt

CLIENT = None
BUCKET = None
JWT = None

def add(args):
    bucket_name = BUCKET
    destination_file = args.get('target', False)
    raw_file = args.get('raw', False)
    text = args.get('text', False)
    if not bucket_name or not destination_file:
        return {'statusCode': 400}
    
    if raw_file:
        # with open(destination_file, 'w') as f:
        #         f.write(raw_file)
        target = f"/{JWT['username']}/{destination_file}"
        CLIENT.put_object(
            bucket_name, target, io.BytesIO(raw_file), length=-1, part_size=10*1024*1024,
        )
        return {'statuCode': 204}
    elif text:
        target = f"/{JWT['username']}/{destination_file}"
        CLIENT.put_object(
            bucket_name, target, io.BytesIO(str.encode(text)), len(text)
        )
        return {'statuCode': 204}
    return {'statusCode': 400}

def find(args):
    global BUCKET
    name = args.get('name', False)
    if not name:
        return {'statusCode': 400}
    try:
        data = CLIENT.get_object(BUCKET, name)
    except ResponseError as err:
        print(err)
    return {"body": data.read()}

def find_all():
    # List objects information whose names starts with "my/prefix/".
    objects = CLIENT.list_objects("gporchia-web", prefix=JWT['username'] + '/')
    arr = []
    for obj in objects:
        arr.append(str(obj.object_name).replace(JWT['username'] + '/', ''))
    return {'statusCode': 200, 'body': arr}

def presigned_url(args):
    name = args.get('name', None)
    access = args.get('MINIO_ACCESS_KEY', None)
    secret = args.get('MINIO_SECRET_KEY', None)
    if name == None or access == None or secret == None:
        return {'statusCode': 400}
    client = Minio('s3.nuvolaris.dev',
        access_key=access,
        secret_key=secret,
        secure=True,
    )
    url = client.presigned_put_object('gporchia-web', name, expires=timedelta(hours=2))
    return {'statusCode': 200, 'body': url}

def main(args):
    global CLIENT
    global BUCKET
    global JWT
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split(' ')[1]
    secret = args.get('JWT_SECRET')
    JWT = jwt.decode(token, key=secret, algorithms='HS256')
    endpoint = f"{args.get('MINIO_HOST')}:{args.get('MINIO_PORT')}"
    CLIENT = Minio('s3.nuvolaris.dev',
        access_key=args.get('MINIO_ACCESS_KEY'),
        secret_key=args.get('MINIO_SECRET_KEY'),
        secure=True,
    )
    path: str = args.get('__ow_path', False)
    path_spl = path[1:].split('/')
    if len(path_spl) != 2:
        return {"statusCode": 400}
    BUCKET = path_spl[0]
    op = path_spl[1]
    found = CLIENT.bucket_exists(BUCKET)
    if not found:
        return {'statusCode': 404, 'body': f'bucket {BUCKET} missing'}
    if op == 'add' and args['__ow_method'] == 'post':
        return add(args)
    # elif path == '/delete' and args['__ow_method'] == 'delete':
    #     return delete(args)
    # elif path == '/update' and args['__ow_method'] == 'put':
    #     return update(args)
    elif op == 'find' and args['__ow_method'] == 'get':
        return find(args)
    elif op == 'presignedUrl' and args['__ow_method'] == 'get':
        return presigned_url(args)
    elif op == 'find_all' and args['__ow_method'] == 'get':
        return find_all()
    return {'statusCode': 404}