#--web true
#--kind python:default
#--annotation provide-api-key true
#--param GPORCHIA_API_KEY $GPORCHIA_API_KEY

from openai import OpenAI
import socket

AI = None
MODEL = "gpt-3.5-turbo"

ROLE="""
You're specialize in creating HTML page
- Answer ONLY with the html page.
- Insert as many tabs as possible and always write to your max_tokens
- If you need to make a request to an endpoint you MUST use javascript. If the action needs parameters, create an <input> for each key. If a parameters is a nested JSON, create an <input> for each key. DELETE AND UPDATE EXPECT THE '_id' NEVER USE OTHER PARAMETERS. example:
<html><head>
    <title>Book CRUD Operations</title>
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
<style>undefined</style><link rel="preconnect" href="https://fonts.googleapis.com" crossorigin="use-credentials"><link rel="preconnect" href="https://fonts.gstatic.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mulish:wght@200;300;400;500;600;700;800;900&amp;display=swa"></head>
<body>
    <h2>Create Book</h2>
    <input type="text" id="createTitle" placeholder="Title">
    <input type="text" id="createAuthor" placeholder="Author">
    <input type="number" id="createPages" placeholder="Pages">
    <input type="number" id="createYear" placeholder="Year">
    <button onclick="createBook()">Create Book</button>
    <div id="createResponse"></div>

    <h2>Update Book</h2>
    <input type="text" id="updateID" placeholder="ID">
    <input type="text" id="updateTitle" placeholder="New Title">
    <input type="text" id="updateAuthor" placeholder="New Author">
    <input type="number" id="updatePages" placeholder="New Pages">
    <input type="number" id="updateYear" placeholder="New Year">
    <button onclick="updateBook()">Update Book</button>
    <div id="updateResponse"></div>

    <h2>Delete Book</h2>
    <input type="text" id="deleteID" placeholder="ID">
    <button onclick="deleteBook()">Delete Book</button>
    <div id="deleteResponse"></div>

    <h2>Find Book</h2>
    <input type="text" id="filterTitle" placeholder="Filter Title">
    <input type="text" id="filterAuthor" placeholder="Filter Author">
    <input type="number" id="filterPages" placeholder="Filter Pages">
    <input type="number" id="filterYear" placeholder="Filter Year">
    <button onclick="findBook()">Find Book</button>
    <div id="findResponse"><br></div>
- While creating javascript requests, always include the code with the correct url. Example:"
function createBook() {
            const title = document.getElementById('createTitle').value;
            const author = document.getElementById('createAuthor').value;
            const pages = document.getElementById('createPages').value;
            const year = document.getElementById('createYear').value;

            // Call to create book endpoint
            obj = {'data': {'title': title, 'author': author, 'pages': pages, 'year': year}}
            fetch('https://nuvolaris.dev/api/v1/web/gporchia/default/create_book', { 
                method: 'POST', 
                body: JSON.stringify(obj),
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.text())
            .then(data => document.getElementById('createResponse').innerText = data);
        }
- If there are requests, make a div to display the return of the API call. This div should be well formatted and aestethical good
- If you don't get both information, you'll answer "I need the action url and the action info to create the HTML"
- include this CSS into the head: '<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">'
- ALWAYS answer directly with <!DOCTYPE html>. No starting quotes
"""

def ask(
    query: str,
    model: str = MODEL,
    print_message: bool = False,
) -> str:
    messages = [
        {"role": "system", "content": ROLE},
        {"role": "user", "content": query},
    ]
    response = AI.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content

TUNED_MODEL = None

def main(args):
    global AI

    AI = OpenAI(api_key=args['GPORCHIA_API_KEY'])

    input = args.get("input", "")
    output = ""
    if input == "":
        output = "Please provide an action to generate the html"
    else:
        output = ask(query=input, print_message=False, model=MODEL)
        output = output.replace("```html", '')
        output = output.replace("```", '')
        # output = output.replace('"', '&quot;')
        print(output)

    res = { "output": output}
    return {"body": res }

