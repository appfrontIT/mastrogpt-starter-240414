
// receive messages and forward to the display method
window.addEventListener('message', async function(ev) {
    let data = ev.data
    // console.log(data);
    fetch("/api/my/mastrogpt/display", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(r => r.text())
    .then(t => {
        if(t !=  "") {
            let content = this. document.getElementById("_display_container_");
            content.innerHTML = t;
        }
    })
    .catch(e => {
        content.innerHTML="<h1>Error!</h1><p>Check logs for details.</p>"
        console.log(e)
    })
})
