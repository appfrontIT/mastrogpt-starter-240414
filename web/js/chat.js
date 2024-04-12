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

// Classes
class Invoker {

  constructor(name, url) {
    this.name = name
    this.url = url
    this.state = null
  }

  async invoke(msg) {
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
    if (this.state != null) {
      json['state'] = this.state
    }
    // send the request
    console.log(this.url)
    return fetch(this.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(json)
    })
      .then(r => r.json())
      .then(r => {
        this.state = r.state
        let data = r
        let login = data.login
        if (login) {
          console.log("login")
          document.getElementById("hybrid").type = "password"
          delete data['login']
        }
        if (data.password) {
          document.getElementById("hybrid").type = "text"
          delete data['password']
        }
        let output = data.output
        delete data['output']
        delete data['state']
        displayWindow.postMessage(data)
        return output
      })
      .catch(e => {
        console.log(e)
        return `ERROR interacting with ${this.url}`
      })
  }
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();
  return `${h.slice(-2)}:${m.slice(-2)}`;
}


function appendMessage(name, img, side, text) {
  //   Simple solution for small apps
  console.log(text)
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

function bot(msg) {
  if (msg == "") {
    return ;
  }
  appendMessage(BOT_NAME, BOT_IMG, "left", msg);
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
  console.log(ev);
  invoker = new Invoker(ev.data.name, ev.data.url)
  titleChat.textContent = ev.data.name
  areaChat.innerHTML = ""
  bot(await invoker.invoke(""))
})
