<div>
  <img alt="walkiria logo" src={appfront_logo} />
  <label class="label">
    <input
    class="input"
    type="text"
    bind:value="{username}"
    name="username"
    placeholder="Enter your Username" required
    data-np-uid="prova"/>
  </label>

  <label class="label">
    <input
    class="input"
    type="password"
    bind:value="{password}"
    name="password"
    placeholder="Enter your Password" required
    data-np-uid="prova"/>
  </label>

    <div>
      <button
      type="button"
      style="width: 100%;"
      class="btn variant-filled" on:click|preventDefault={login}>Login</button>
    </div>
</div>

<script lang="ts">
import appfront_logo from '$lib/appfront_logo.png'
import { onMount } from 'svelte';
import { user } from '../../store';

let username: string;
let password: string;

async function login() {
    const response: Response = await fetch('api/my/base/auth/login', {
      method: 'POST',
      credentials: 'include',
      body: JSON.stringify({'username': username, 'password': password}),
      headers: { 'Content-Type': 'application/json' },
    })
    if (response.status == 200) {
      const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })
      if (res.ok) { const obj = await res.json(); $user = obj; return window.location.assign('/'); }
      else { throw new Error('failed to get user') };
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
      else { throw new Error('failed to get user') };
    }
  }
})

</script>

<style>
  /*index.css*/
:global(body) {
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: sans-serif;
    line-height: 1.5;
    min-height: 100vh;
    background: #f3f3f3;
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