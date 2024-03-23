//--web true
//--kind nodejs:default

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
    appendMessage(BOT_NAME, BOT_IMG, "left", msg);
}

window.addEventListener('message', async function (ev) {
    console.log(ev);
    invoker = new Invoker(ev.data.name, ev.data.url)
    titleChat.textContent = ev.data.name
    areaChat.innerHTML = ""
    bot(await invoker.invoke(""))
})

async function main() {
    return "hello world!"
    let input = args.text || ""
    console.log("input " + input)
    if (input != "") {
        bot(input)
    }
}