<div>
    <img alt="walkiria logo" src={appfront_logo} />
    <label class="label">
        <input
        class="input"
        type="text"
        bind:value="{name}"
        name="name"
        placeholder="name" required
        data-np-uid="prova"/>
    </label>
    <label class="label">
        <input
        class="input"
        type="text"
        bind:value="{surname}"
        name="surname"
        placeholder="surname" required
        data-np-uid="prova"/>
    </label>
    <!-- <label class="label">
        <input
        class="input"
        type="password"
        bind:value="{password}"
        name="password"
        placeholder="Password" required
        data-np-uid="prova"/>
    </label> -->
    <label class="label">
        <input
        class="input"
        type="text"
        bind:value="{username}"
        name="username"
        placeholder="username" required
        data-np-uid="prova"/>
    </label>
    <label class="label">
        <input
        class="input"
        type="email"
        bind:value="{email}"
        name="email"
        placeholder="email" required
        data-np-uid="prova"/>
    </label>
    <div class="text-center space-y-2">
        <button type="button" style="width: 100%;" class="btn variant-filled" on:click|preventDefault={signup}>signup</button>
        <p>already a member? <a href="/login">login</a></p>
    </div>
</div>

<script lang="ts">
import appfront_logo from '$lib/assets/appfront_logo.png'
import { onMount } from 'svelte';
import { user } from '../../store';

let name: string;
let surname: string;
let username: string;
// let password: string;
let email: string;

const validateEmail = (email) => {
    return email.match(
        /^\S+@\S+\.\S+$/
    );
};

async function signup() {
    if (!name || !surname || !username || !email) { alert("compile all fields before submitting!"); return ;}
    if (!validateEmail(email)) { alert("pleas, insert a valid email"); return ;}
    const response: Response = await fetch('api/my/base/auth/signup', {
        method: 'POST',
        body: JSON.stringify({'name': name, 'surname': surname, 'username': username, 'email': email}),
        headers: { 'Content-Type': 'application/json' },
    })
    if (response.status == 200) {
        alert('Your signup request was sending. Please wait until the validation before logging in!')
    } else {
        const text = await response.text();
        alert(text);
    }
}

onMount(async () => {
    let cookie = document.cookie;
    if (cookie) {
        const split_cookie = cookie.split('=');
        if (split_cookie[0] === 'appfront-sess-cookie') {
            const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })
        if (res.ok) { const obj = await res.json(); $user = obj; return window.location.assign('/'); }
        else {
            document.cookie = 'appfront-sess-cookie=;expires=Thu, 01 Jan 1970 00:00:01 GMT';
            sessionStorage.clear();
            throw new Error('failed to get user');
            };
        }
    }
})

</script>

<style>

:global(body) {
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: sans-serif;
    line-height: 1.5;
    min-height: 100vh;
    background: #ffffff;
    flex-direction: column;
    margin: 0;
}

:global(label) {
    display: block;
    width: 100%;
    margin-top: 10px;
    margin-bottom: 5px;
    text-align: left;
    color: #555;
    font-weight: bold;
}

input {
    display: block;
    width: 100%;
    margin-bottom: 15px;
    padding: 10px;
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 5px;
}

</style>