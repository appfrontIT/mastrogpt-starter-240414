import os

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

ROLE="""
You're a frontend developer. You develop only using HTML/CSS/JS.
You develop interface to interact with Nuvolaris/OpenWhisk actions.

Here some things you must care about:
  1 - If the user wants to implement some actions, you must very carefully read and understand all the actions, all the urls and the returns of the actions, to generate correct html
  2 - If you need to make a request to an endpoint you MUST use javascript. Remember: the endpoints are inside the actions passed
  3 - Obviously, you must implement everything, all the script and all the html sections. This includes each fetch, document and so on. This is mandatory!
  4 - Incorpote CSS into the page, with extensive style and customization
  5 - ALWAYS answer directly with <!DOCTYPE html>. No starting quotes
  6 - if the action needs authorization, you can get the token using the cookie. Here's a full example on how to do it:
      - let cookie = document.cookie; if (!cookie) return window.location.assign('/login');
      - response = await fetch('https://nuvolaris.dev/api/v1/web/gporchia/base/auth/token?cookie=' + cookie, {method: 'GET'});
      - if (response.ok) { const obj = await response.json(); const token = obj['token']}
    Include the token as a 'Bearer'

You answer returns the HTML. NOTHING ELSE MUST BE RETURNED.
If you need to display prompts to insert data to send to an URL, use and input text and then send data using javascript. You also must create a section to display the return. Again: be very carefull about the action returns. Consider everything between ``` as an example. Be carefull to set the correct fields and url:
- example with single fetch return:
```
<h1>Multiply by 2</h1>
<input type="text" id="numberInput" placeholder="Enter a number">
<button onlick="multiplyBy2()">Multiply by 2</button>
<div id="Response"></div>
<script>
  function multiplyBy2() {
    const number = document.getElementById('numberInput').value;
      fetch('https://nuvolaris.dev/api/v1/web/gporchia/pippo/multiply_by_2', {
        method: 'POST',
        body: JSON.stringify({ 'number': number }),
        headers: { 'Content-type': 'application/json; charset=UTF-8' },
        })
        .then(response => response.json())
        .then(data => {
          document.getElementById('Response').innerHTML = `Result: ${data}`;
          })
        .catch(error => console.error('Error:', error));
        }
</script>
```
- If you have to call the database, you must use this endpoint. Consider everything between '<>' parameter to change: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/<collection>/<operation>
operations possible are:
  - add: method 'POST'. this operation require parameter data like {'data': <data>}
  - add_many: method 'POST'. this operation require parameter data with array as value like {'data': [<data1>, <data2>, <data3>, ...]}
  - find_one: method 'GET'. this operation accepts query params to filter search and return. Example: 'https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/<collection>/find?filter=' + encodeURIComponent(JSON.stringify(<filter to search>) + '&fields'+ + encodeURIComponent(JSON.stringify(<fields to return>). Return a single object
  - find_many: method 'GET'. this operation accepts query params to filter search and return and number of elements returned. Example: 'https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/<collection>/find?filter=' + encodeURIComponent(JSON.stringify(<filter to search>) + '&fields'+ + encodeURIComponent(JSON.stringify(<fields to return>) + '&n_results=<n>'. Return an array of objects
  - delete: method 'DELETE'. this operation accepts query param id: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/<collection>/delete?id=<id>
  - update: method 'PUT'. This operation accepts query param id and parameter data as body: https://nuvolaris.dev/api/v1/web/gporchia/db/mongo/mastrogpt/<collection>/update?id=<id>, body: JSON.stringify({'data': <data>}). Returns the updated user
"""

html_crud = """
<body>
<section>
<nav>
<h5>Create {model}</h5>
<input type="text" id="create{model field 1}" placeholder="{model field 1}">
<input type="text" id="create{model field 2}" placeholder="{model field 2}">
<input type="text" id="{model field 3}" placeholder="{model field 3}">
<input type="tel" id="{model field 4}" placeholder="{model field 4}">
<input type="number" id="{model field 5}" placeholder="{model field 5}">
<button onclick="create{model}()">Create {model}</button>
<h5>Update {model}</h5>
<input type="text" id="updateId" placeholder="Id">
<input type="text" id="update{model field 1}" placeholder="{model field 1}">
<input type="text" id="update{model field 2}" placeholder="{model field 2}">
<input type="text" id="update{model field 3}" placeholder="{model field 3}">
<input type="tel" id="update{model field 4}" placeholder="{model field 4}">
<input type="number" id="update{model field 5}" placeholder="{model field 5}">
<button onclick="update{model}()">Update {model}</button>
<h5>Delete {model}</h5>
<input type="text" id="deleteFilter" placeholder="Filter Info">
<button onclick="delete{model}()">Delete {model}</button>
<h5>Find {model}</h5>
<input type="text" id="filter{model field 1}" placeholder="{model field 1}">
<input type="text" id="filter{model field 2}" placeholder="{model field 2}">
<input type="text" id="filter{model field 3}" placeholder="{model field 3}">
<input type="tel" id="filter{model field 4}" placeholder="{model field 4}">
<input type="number" id="filter{model field 5}" placeholder="{model field 5}">
<button onclick="find{model}()">Find {model}</button>
</nav>
<article id="Response"><br>
</article>
</section>
<script>
function create{model}() {
const {model field 1} = document.getElementById('create{model field 1}').value;
const {model field 2} = document.getElementById('create{model field 2}').value;
const {model field 3} = document.getElementById('create{model field 3}').value;
const {model field 4} = document.getElementById('create{model field 4}').value;
const {model field 5} = document.getElementById('create{model field 5}').value;
fetch('https://nuvolaris.dev/api/v1/web/gporchia/base/{action to create element}', {
method: 'POST',
body: JSON.stringify({ {model field 1}: {model field 1}, {model field 2}: {model field 2}, {model field 3}: {model field 3}, {model field 4}: {model field 4}, {model field 5}: {model field 5} }),
headers: { 'Content-type': 'application/json; charset=UTF-8' },
})
.then(response => response.json())
.then(data => {
var to_display = "<ul>"
  for (var key in data) {
var name = key;
var value = data[key].toString();
    to_display += `<li>${name}: ${value}</li>`
  }
to_display += "</ul>"
document.getElementById('Response').innerHTML = to_display;
});
}
function update{model}() {
const id = document.getElementById('updateId').value;
const {model field 1} = document.getElementById('update{model field 1}').value;
const {model field 2} = document.getElementById('update{model field 2}').value;
const {model field 3} = document.getElementById('update{model field 3}').value;
const {model field 4} = document.getElementById('update{model field 4}').value;
const {model field 5} = document.getElementById('update{model field 5}').value;
fetch('https://nuvolaris.dev/api/v1/web/gporchia/base/{action to update element}', {
method: 'PUT',
body: JSON.stringify({ filter: {_id: id}, {model field 1}: {model field 1}, {model field 2}: {model field 2}, {model field 3}: {model field 3}, {model field 4}: {model field 4}, {model field 5}: {model field 5} }),
headers: { 'Content-type': 'application/json; charset=UTF-8' },
})
.then(response => response.json())
.then(data => {
var to_display = "<ul>"
  for (var key in data) {
var name = key;
var value = data[key].toString();
    to_display += `<li>${name}: ${value}</li>`
  }
to_display += "</ul>"
document.getElementById('Response').innerHTML = to_display;
});
}
function delete{model}() {
const id = document.getElementById('deleteFilter').value;
fetch('https://nuvolaris.dev/api/v1/web/gporchia/base/{action to delete element}', {
method: 'DELETE',
body: JSON.stringify({ filter: {_id: id}}),
headers: { 'Content-type': 'application/json; charset=UTF-8' },
})
.then(response => response.json())
.then(data => {
var to_display = "<ul>"
  for (var key in data) {
var name = key;
var value = data[key].toString();
    to_display += `<li>${name}: ${value}</li>`
  }
to_display += "</ul>"
document.getElementById('Response').innerHTML = to_display;
});
}
function find{model}() {
const {model field 1} = document.getElementById('filter{model field 1}').value;
const {model field 2} = document.getElementById('filter{model field 2}').value;
const {model field 3} = document.getElementById('filter{model field 3}').value;
const {model field 4} = document.getElementById('filter{model field 4}').value;
const {model field 5} = document.getElementById('filter{model field 5}').value;
fetch('https://nuvolaris.dev/api/v1/web/gporchia/base/{action to find element}', {
method: 'POST',
body: JSON.stringify({ filter: {{model field 1}: {model field 1}, {model field 2}: {model field 2}, {model field 3}: {model field 3}, {model field 4}: {model field 4}, {model field 5}: {model field 5}} }),
headers: { 'Content-type': 'application/json; charset=UTF-8' },
})
.then(response => response.json())
.then(data => {
var to_display = "<ul>"
for (var i = 0; i < data.length; i++) {
var element = JSON.parse(data[i]);
  for (var key in element) {
var name = key;
var value = element[key].toString();
    to_display += `<li>${name}: ${value}</li>`
  }
    to_display += "<br />"
}
to_display += "</ul>"
document.getElementById('Response').innerHTML = to_display;
});
}
</script>
</body>
"""