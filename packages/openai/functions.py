#--web true

def main(args):
    print(args)
    name = args.get('name')
    print(name)
    return {"body": "ok"}