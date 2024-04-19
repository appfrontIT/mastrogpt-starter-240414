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
fetch('https://nuvolaris.dev/api/v1/web/gporchia/default/{action to create element}', {
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
fetch('https://nuvolaris.dev/api/v1/web/gporchia/default/{action to update element}', {
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
fetch('https://nuvolaris.dev/api/v1/web/gporchia/default/{action to delete element}', {
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
fetch('https://nuvolaris.dev/api/v1/web/gporchia/default/{action to find element}', {
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