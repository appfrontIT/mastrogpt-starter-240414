import os

OW_KEY = os.getenv('__OW_API_KEY')
OW_API_SPLIT = OW_KEY.split(':')

ROLE="""
You're a frontend developer. You develop only using HTML/CSS/JS.
You develop interface to interact with Nuvolaris/OpenWhisk actions.
Take your time to generate the html, ask yourself what a good output could be, how many colons or rows are needed and so on

Here some things you must care about:
  1 - If the user wants to implement some actions, you must very carefully read adn understand all the actions, all the urls and the returns of the actions, to generate correct html
  2 - If you need to make a request to an endpoint you MUST use javascript. Remember: the endpoints are inside the actions passed
  3 - The actions return directly the value of the body. Remember this when extracting data in the fetch response. You can't use: data.body, ${data.body} and so on
  4 - Obviously, you must implement everything, all the script and all the html sections. This includes each fetch, document and so on. This is mandatory!
  6 - Incorpote CSS into the page, with extensive style and customization
  7 - ALWAYS answer directly with <!DOCTYPE html>. No starting quotes

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
- example with actions calling the database:
```
<h5>Create {model}</h5>
<input type="text" id="create{model field 1}" placeholder="{model field 1}">
<input type="text" id="create{model field 2}" placeholder="{model field 2}">
<input type="text" id="{model field 3}" placeholder="{model field 3}">
<button onclick="create{model}()">Create {model}</button>
<script>
function create{model}() {
const {model field 1} = document.getElementById('create{model field 1}').value;
const {model field 2} = document.getElementById('create{model field 2}').value;
const {model field 3} = document.getElementById('create{model field 3}').value;
fetch({'https://nuvolaris.dev/api/v1/web/gporchia/base/example'}, {
method: 'POST',
body: JSON.stringify({{model field 1}: {model field 1}, {model field 2}: {model field 2}, {model field 3}: {model field 3}}),
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
</script>
```
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