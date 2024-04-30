#--web true
#--kind python:default

import chevron
import traceback

def render(src, args):
    with open(src) as f:
        return chevron.render(f, args)
    
def main(args):
    out = ""

    if "html" in args:
        out = render("html.html", args)
    elif "message" in args:
        if not "title" in args:
            args["title"] = "Message"
        out = render("message.html", args)

    code = 200 if out != "" else 204
    return {
        "body": out,
        "statusCode": code
    }