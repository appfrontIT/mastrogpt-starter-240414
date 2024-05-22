let base = location.href.replace(/index\.html$/, "")

window.addEventListener("DOMContentLoaded", (event) => {
    let cookie = document.cookie;
    if (cookie) {
        window.location.assign('/selector.html')
    }
    const form = document.getElementById('submit-form');
    form.addEventListener("submit", onFormSubmit);
    
    async function onFormSubmit(event) {
        event.preventDefault();
        const data = new FormData(event.target);
        const user = data.get('username');
        const password = data.get('password');
        try {
            const response = await fetch(base+'api/my/base/auth/login', {
                method: 'POST',
                credentials: 'include',
                body: JSON.stringify({'username': user, 'password': password}),
                headers: { 'Content-Type': 'application/json' },
            })
            const obj = await response.json();
            if (response.status == 200) {
                return window.location.assign('/selector.html')
            }
        } catch (error) {
            console.log(error)
        }
    }
})

