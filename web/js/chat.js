// Globals
let invoker = undefined

// Constants
const BOT_IMG = "/img/hari.png";
const PERSON_IMG = "/img/human-mini.png";
const BOT_NAME = "Hari";
const PERSON_NAME = "YOU";

// Page compoents
const msgerForm = document.querySelector(".msger-inputarea");
const msgerInput = document.querySelector(".msger-input");
const msgerChat = document.querySelector(".msger-chat");
const titleChat = document.getElementById("chat-title");
const areaChat = document.getElementById("chat-area");
const displayWindow = window.parent.document.getElementById("display").contentWindow
let base = location.href.replace(/chat\.html$/, "")

// Classes
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class Invoker {

  constructor(name, url) {
    this.name = name
    this.url = url
  }


  async invoke(msg) {
    let cookie = document.cookie;
    if (!cookie) {
      alert('error: session expired')
      window.parent.location.replace('/index.html')
    }
    // welcome message no input
    if (msg == null) {
      return "Welcome, you have selected " + this.name;
    }
    // no url 
    if (this.url == null)
      return "Welcome, please select the chat application you want to use by clicking a  button on top.";
    // prepare a request
    let json = {
      input: msg,
      // history: history
    }
    // send the request
    try {
      let response = await fetch(this.url, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(json),
      });
      console.log(response.status)
      switch (response.status) {
        case 204: return response
        case 403: alert("Non hai l'autorizzazione per accedere questa sezione"); return response;
        case 200: {
          const data = await response.json()
          if (data['logout']) {
            document.cookie = data['cookie'] + '=;expires=Thu, 01 Jan 1970 00:00:01 GMT'
            return window.parent.location.replace('/index.html')
          }
        }
        default: break;
      }
      return response
    } catch (error) {
      console.log(error)
    }
  }
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();
  return `${h.slice(-2)}:${m.slice(-2)}`;
}


function appendMessage(name, img, side, text) {
  //   Simple solution for small apps
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
        <div class="msg-text">${html}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

async function bot() {
  url = base+'api/my/db/chat'
  while (true) {
    try {
      let r = await fetch(url, {method: 'GET', headers: {
        "Content-Type": "application/json"
      },
      credentials: "include"
      })
      console.log(r.status)
      if (r.status == 204) {
        continue;
      } else {
        const obj = await r.json()
        let chat = obj.chat
        for (let j = 0; j < chat.length; j++) {
          let data = chat[j];
          let output = data.output
          delete data['output']
          displayWindow.postMessage(data)
          if (output != "") {
            appendMessage(BOT_NAME, BOT_IMG, "left", output);
          }
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


msgerForm.addEventListener("submit", event => {
  event.preventDefault();

  const input = msgerInput.value;
  if (!input) return;
    human(input);

  if (invoker) {
    invoker.invoke(input).then(reply => bot(reply))
  } else {
    bot("Please select a chat, clicking on one button on the top area.")
  }
});

window.addEventListener('message', async function (ev) {
  // document.getElementById("hybrid").type = "text"
  invoker = new Invoker(ev.data.name, ev.data.url)
  titleChat.textContent = ev.data.name
  areaChat.innerHTML = ""
  await invoker.invoke("")
  bot()
})
