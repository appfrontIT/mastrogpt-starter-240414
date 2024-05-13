// global variables
let chat = document.getElementById("chat").contentWindow
let display = document.getElementById("display").contentWindow
let base = location.href.replace(/selector\.html$/, "")

// inizialize the chat buttons
document.addEventListener("DOMContentLoaded", async function() {
    let x = document.cookie;
    if (!x) {
        return window.location.assign('/index.html')
    }
    const token_response = await fetch(base + 'api/my/default/auth/token', {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json'},
    })
    if (!token_response.ok) {
        document.cookie = 'appfront-sess-cookie=;expires=Thu, 01 Jan 1970 00:00:01 GMT'
        return window.location.assign('/index.html')
    }
    // retrieve index
    fetch(base+"api/my/mastrogpt/index")
    .then( (x)  => x.json())
    .then( (data) => {
        let insert = document.getElementById("top-area")
        data.services.forEach(service => {
            const button = document.createElement("button");
            button.textContent = service.name;
            button.onclick = function() {
                let url = base + "api/my/"+service.url
                chat.postMessage({name: service.name, url: url})
            };
            let = p = document.createElement("span")
            p.appendChild(button);
            insert.appendChild(p);
        });
    })
    .catch( (e) => { console.log(e); alert("ERROR:  index") } )
})
