// Globals
let invoker = undefined

// Constants
const BOT_IMG = "/img/hari.png";
const PERSON_IMG = "/img/human-mini.png";
const BOT_NAME = "Hari";
const PERSON_NAME = "YOU";
let token = undefined

// Page compoents
const msgerForm = document.querySelector(".msger-inputarea");
const msgerInput = document.querySelector(".msger-input");
const msgerChat = document.querySelector(".msger-chat");
// const titleChat = document.getElementById("chat-title");
const areaChat = document.getElementById("chat-area");
var display = parent.document.getElementById("display")
const displayWindow = window.parent.document.getElementById("display").contentWindow
const displayFrame = window.parent.document.getElementById("display")
let base = location.href.replace(/chat\.html$/, "")
let g_url;

async function forward_msg(msg) {
  let json = { input: msg }
  try {
    let response = await fetch(g_url, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token},
      body: JSON.stringify(json),
    });
    switch (response.status) {
      case 204: return response
      case 403: alert("Non hai l'autorizzazione per accedere questa sezione"); return response;
      case 404: {
        const data = await response.json()
        alert('error: session expired');
        return window.parent.location.replace('/index.html');}
      case 200: {};
      default: break;
    }
    return response
  } catch (error) {
    console.log(error)
  }
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();
  return `${h.slice(-2)}:${m.slice(-2)}`;
}


function appendMessage(name, img, side, text) {
  //   Simple solution for small apps
  // var converter  = new showdown.Converter()
  // let html = converter.makeHtml(text);
  let html = marked.parse(text)
  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">
            <div class="msg-img" style="background-image: url(${img})"></div>
            <span>${name}</span>
          </div>
          <div class="msg-info-time"> ${formatDate(new Date())}</div>
        </div>
        <div class="msg-text"><code>${html}</code></div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

async function bot() {
  const url = base+'api/my/db/chat'
  const user = sessionStorage.getItem('user')
  user_obj = JSON.parse(user)
  appendMessage(BOT_NAME, BOT_IMG, "left", `Bentornato ${user_obj['username']}! Come posso aiutarti?`);
  while (true) {
    try {
      let r = await fetch(url, {method: 'GET', headers: {
        "Content-Type": "application/json"
      },
      credentials: "include"
      })
      if (r.status == 204) {
        continue;
      } else {
        const chat = await r.json()
        for (let j = 0; j < chat.length; j++) {
          let data = chat[j];
          if ('frame' in data) {
            displayFrame.src = data.frame
            delete data['frame']
          }
          if ('editor' in data) {
            displayWindow.postMessage({'editor': data.editor})
            delete data['editor']
          }
          if ('output' in data) {
            output = data.output;
            if (output != "") {
              appendMessage(BOT_NAME, BOT_IMG, "left", output);
            }
            delete data['output'];
          }
          displayWindow.postMessage(data)
        }
      }
    } catch(error) {
      console.log(error)
      return `ERROR interacting with ${this.url}`
    }
  }
}

function human(msg) {
  appendMessage(PERSON_NAME, PERSON_IMG, "right", msg);
  msgerInput.value = "";
}

msgerForm.addEventListener("submit", async event => {
  event.preventDefault();

  const input = msgerInput.value;
  if (!input) return;
  
  human(input);
  forward_msg(input)
});

window.addEventListener('message', load_chat)

async function load_chat(ev) {
  if (!ev.data.url || ev.data.url == undefined) return;
  g_url = ev.data.url;
  let cookie = document.cookie;
  if (!cookie) {
    alert('error: session expired')
    window.parent.location.replace('/index.html')
  } else {
    const response = await fetch(base + 'api/my/base/auth/token', {
      method: 'GET',
      credentials: 'include'
    })
    if (response.ok) {
      const obj = await response.json()
      token = obj['token']
    }
  }
  areaChat.innerHTML = ""
  forward_msg("");
  bot();
}
