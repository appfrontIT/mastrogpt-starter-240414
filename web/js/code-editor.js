var action_package = document.getElementById('action_package')
var action_name = document.getElementById('action_name')
var description = document.getElementById('description')
var lang = document.getElementById('lang')
let base = location.href.replace(/code-editor\.html$/, "");
let action = null;
lang.onchange = langListener;

document.getElementById('editor').style.fontSize='12px';
ace.require("ace/ext/language_tools");
var editor = ace.edit("editor");
editor.setTheme("ace/theme/twilight");
editor.session.setMode("ace/mode/html");
editor.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: false
});

function langListener() {
    editor.session.setMode("ace/mode/" + this.value);
    if (this.value === 'html') {
        action_package.setAttribute("disabled","disabled");
        action_package.style.display = 'none';
        description.setAttribute("disabled","disabled");
        description.style.display = 'none';
        document.getElementById('test').setAttribute("disabled","disabled");
        document.getElementById('test').style.display = 'none';
    } else {
        action_package.removeAttribute("disabled");
        action_package.style.display = 'block';
        description.removeAttribute("disabled");
        description.style.display = 'block';
        document.getElementById('test').removeAttribute("disabled");
        document.getElementById('test').style.display = 'block';
    }
}

document.addEventListener("DOMContentLoaded", async function() {
    const user = sessionStorage.getItem('user')
    var user_obj = await JSON.parse(user)
    const packages = user_obj['package']
    for (var i = 0; i < packages.length; i++) {
        var opt = document.createElement('option');
        opt.value = packages[i];
        opt.innerHTML = packages[i];
        action_package.appendChild(opt);
    }
    const editor = sessionStorage.getItem('editor');
    const editor_obj = await JSON.parse(editor);
    window.postMessage(editor_obj);
    sessionStorage.removeItem('editor')
})

window.addEventListener('message', async function (ev) {
    const data = ev.data.editor
    if (!data) return ;
    if (data['language'] === 'html') {
        for(var i, j = 0; i = lang.options[j]; j++) {
            if(i.value == data['language']) {
                lang.selectedIndex = j;
                break;
            }
        }
        action_name.value = data['name'];
        action_package.setAttribute("disabled","disabled");
        action_package.style.display = 'none';
        description.setAttribute("disabled","disabled");
        description.style.display = 'none';
        document.getElementById('test').setAttribute("disabled","disabled");
        document.getElementById('test').style.display = 'none';
        editor.setValue(data['function']);
        return ;
    }
    action = data;
    action_package.value = data['package']
    action_name.value = data['name']
    description.value = data['description']
    if (data['language'] == 'nodejs') {
        data['language'] = 'javascript';
    }
    for(var i, j = 0; i = lang.options[j]; j++) {
        if(i.value == data['language']) {
            lang.selectedIndex = j;
            break;
        }
    }
    editor.session.setMode("ace/mode/" + data['language']);
    editor.setValue(data['function']);
})

async function deploy() {
    const user = sessionStorage.getItem('user')
    user_obj = await JSON.parse(user)
    token = user_obj['JWT'];
    if (lang.value === "html") {
        if (action_name.value === "") { alert('Provide a name for the page'); return; }
        response = await fetch('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/add', {
            method: "POST",
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
            body: JSON.stringify({"target": action_name.value + ".html", "text": editor.session.getValue()})
        })
        if (response.status == 204) {
            alert('page succesfully uploaded!')
        }
        return ;
    }
    if (action_name.value === "" || description.value === "" || lang.value === "Language" || action_package.value === "") {
        alert('You must fill all fields before deploying an action')
        return ;
    }
    var package = await fetch(base + 'api/my/base/package/find?name=' + action_package.value, {
        method: 'GET',
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    })
    if (package.status != 200) {
        var confirm_package = confirm(`The package ${await action_package.value} does not exist, do you wanna create it?`)
        if (confirm_package) {
            create_package = await fetch(base + 'api/my/base/package/add', {
                method: 'POST',
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
                body: JSON.stringify({"name": await action_package.value})
            })
            if (create_package.status != 200) {
                alert('there was an error while creating your package.')
                return;
            }
            const packages = user_obj['package']
            action_package.reset();
            for (var i = 0; i < packages.length; i++) {
                var opt = document.createElement('option');
                opt.value = packages[i];
                opt.innerHTML = packages[i];
                action_package.appendChild(opt);
            }
        } else {
            return ;
        }
    }
    const func = await editor.session.getValue()
    upload = await fetch(base+'api/my/base/action/add', {
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method: "PUT",
        body: JSON.stringify({
            "name": action_name.value,
            "function": func,
            "description": description.value,
            "namespace": "gporchia/" + package.value,
            "package": action_package.value,
            "language": lang.value
        })
    })
    if (upload.status == 200) {
        alert('action succesfully deployed!')
    }
}

async function verify() {
    const user = sessionStorage.getItem('user')
    user_obj = await JSON.parse(user)
    token = user_obj['JWT'];
    const func = await editor.session.getValue()
    let query = "analizza il codice seguente e mostrami se e dove ci sono degli errori, in piú suggerisci dei miglioramenti se ne hai.\nCodice:\n" + func;
    const r = await fetch(base + 'api/my/base/invoke/walkiria', {
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method: 'POST',
        body: JSON.stringify({"input": query})
    })
}

async function test() {
    if (action_name.value === "" || action_package.value === "") {
        alert('I need the package and the action name to perform the tests');
        return ;
    }
    const user = sessionStorage.getItem('user');
    user_obj = await JSON.parse(user);
    token = user_obj['JWT'];
    const action = await fetch(base + `api/my/base/action/find?package=${action_package.value}&name=${action_name.value}`, {
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method: 'GET'
    })
    if (action.status == 404) {
        var confirm_deploy = confirm('The action must be deployed to perform the tests. Do you wanna deploy it?')
        if (confirm_deploy) {
            await this.deploy();
        } else {
            return ;
        }
    }
    let query = `esegui i test sulla seguente azione: nome: ${action_name.value}, package: ${action_package.value}. Non chiedere conferma e comincia subito con i test`;
    const r = await fetch(base + 'api/my/base/invoke/walkiria', {
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method: 'POST',
        body: JSON.stringify({"input": query})
    })
}

let watch_toggle = false;
async function watch() {
    if (watch_toggle) {
        watch_toggle = false;
        btn = document.getElementById('watch');
        btn.style.backgroundColor = "white";
        btn.style.color = "violet";
        const r = await fetch(base + 'api/my/base/invoke/walkiria', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
            method: 'POST',
            body: JSON.stringify({"input": "grazie del supporto. Esci dalla modalitá 'watch'"})
        })
        return;
    }
    watch_toggle = true
    btn = document.getElementById('watch');
    btn.style.backgroundColor = "#e6e6e6";
    btn.style.color = "white";
    const user = sessionStorage.getItem('user');
    user_obj = JSON.parse(user);
    token = user_obj['JWT'];
    const func = await editor.session.getValue()
    let query = "da ora in poi, considerati in modalitá 'watch', fintanto che non ti comunicheró di smettre. Ti invieró periodicamente dei frammenti di codice. Osserva il codice, e se necessario comunicami gli errori e suggeriscimi le modifiche. Rsipondi con messaggi sintetici e concisi. Se pensi che vada tutto bene, rispondi in pochissime parole che il codice sembra corretto. Comincia chiedendomi che tipo di azione voglio creare. Inoltre, leggi attentamente i commenti per capire cosa il codice dovrebbe fare.";
    const r = await fetch(base + 'api/my/base/invoke/walkiria', {
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method: 'POST',
        body: JSON.stringify({"input": query})
    })
    while (watch_toggle) {
        await new Promise(r => setTimeout(r, 20000));
        const func = await editor.session.getValue()
        if (func === "") { continue; }
        const r = await fetch(base + 'api/my/base/invoke/walkiria', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
            method: 'POST',
            body: JSON.stringify({"input": func})
        })
    }
}

async function display_action() {
    const user = sessionStorage.getItem('user');
    user_obj = await JSON.parse(user);
    token = user_obj['JWT'];
    const r = await fetch(base + 'api/my/base/action/find_all', {
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        method: 'GET',
    });
    if (r.status == 200) {
        obj = await r.json();
        let html = `<html>
        <body>`;
        for (let i = 0; i < obj.length; i++) {
            // div = await JSON.stringify(obj[i]);
            let annotations = obj[i]['annotations']
            let description = 'no description';
            for (let j = 0; j < annotations.length; j++) {
                if (annotations[j]['key'] === 'description') {
                    description = annotations[j]['value'];
                    break ;
                }
            }
            html += `
            <div>Package: ${obj[i]['package']}<br>Name: ${obj[i]['name']}<br>Description: ${description}</div><br>`
        }
        html += `
        </body></html>`;
        let newWin = window.open("about:blank", "actions", "popup=true");
        newWin.document.write(html);
        
    }
}