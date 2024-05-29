#--web true
#--kind python:default
#--annotation description "This action returns an html page to display the crawled pages"

from pymongo import MongoClient
import json
from bson.objectid import ObjectId
import requests

def main(args):
    token = args['__ow_headers'].get('authorization', False)
    if not token:
        return {'statusCode': 401}
    token = token.split('=')[1]
    client = MongoClient("mongodb+srv://matteo_cipolla:ZULcZBvFCfZMScb6@cluster0.qe7hj.mongodb.net/mastrogpt?retryWrites=true&w=majority&appName=Cluster0")
    dbname = client['mastrogpt']
    collection_list = dbname.list_collection_names()
    crawled_pages = []
    for col in collection_list:
        if 'crawl' in col:
            crawled_pages.append(col)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL List with Popup Sections</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f6f8;
                color: #333;
            }
            #container {
                display: flex;
                min-height: 100vh;
            }
            #urlList {
                flex: 0 0 20%; /* Adjusts the width of the URL list */
                background-color: #ffffff;
                padding: 20px;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                border-radius: 8px;
                margin-top: 20px;
            }
            #urlList ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            #urlList li a {
                display: block;
                padding: 10px;
                text-decoration: none;
                color: #007BFF;
                transition: background-color 0.3s, color 0.3s;
            }
            #urlList li a:hover, #urlList li a:focus {
                background-color: #007BFF;
                color: #ffffff;
            }
            #contentArea {
                flex: 1;
                padding: 40px;
                background-color: #e9ecef;
            }
            .card {
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="urlList">
                <h2>URLs List</h2>
                <ul>"""
    for url in crawled_pages:
        domain = url.replace('cawl__', '').replace('__', '.').replace('_', '-')
        html += f"""<li><a href="#" onclick="showPopup('{url}')">{domain}</a></li>"""
    html +=f"""</ul>
            </div>
            <div id="popup">
            </div>
        </div>
        <script>
            function showPopup(id) {{
                // Show the selected popup
                fetch('https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/' + id + '/find_many', {{
                method: 'GET',
                headers: {{ 'Content-type': 'application/json; charset=UTF-8', 'Authorizatino': 'Bearer {token}' }},
                }})
                .then(response => response.json())
                .then(data => {{
                node = document.getElementById('popup')
                node.textContent = '';
                for (let i = 0; i < data.length; i++) {{
                    let obj = data[i]
                    let section = document.createElement('div');
                    section.classList.add('card')
                    to_display = "<ul>"
                    for (var key in obj) {{
                        var name = key;
                        if (name == 'ID') {{ continue; }}
                        var value = obj[key].toString();
                        to_display += `<li><h2>${{name}}</h2><br>${{value}}</li>`
                    }}
                    to_display += "</ul>"
                    section.innerHTML = to_display    
                    node.appendChild(section);
                }}
            }});
            }}
        </script>
        </body>
        </html>
    """

    return {"body": html}