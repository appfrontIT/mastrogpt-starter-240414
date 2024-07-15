<script lang="ts">
    import { LightSwitch } from '@skeletonlabs/skeleton';
    import { onMount } from 'svelte';
    import * as swaggerJson from '$lib/appfront.json';
    import SwaggerUI from 'swagger-ui';
    import 'swagger-ui/dist/swagger-ui.css';
    import { user, logged } from '../../store'

    let paths = [];
    let curr_path;
    onMount(async () => {
        let cookie = document.cookie;
        if (!cookie) {
			return window.location.assign('/login')
        } else if (cookie) {
			const split_cookie = cookie.split('=');
			if (split_cookie[0] != 'appfront-sess-cookie') {
				return window.location.assign('/login')
			}
		}
		$logged = true;
        if (!$user) {
            const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })
            if (res.ok) { const obj = await res.json(); $user = obj; }
            else {
                return window.location.assign('/login');
            };
        }
        const yaml = await fetch('api/my/base/openAPI/get', {
            method: 'GET',
            headers: {'Authorization': `Bearer ${$user.JWT}`}
        })
        const obj = await yaml.json();
        paths = Object.entries(obj['paths']);
        SwaggerUI({
            spec: obj,
            dom_id: '#swagger-ui-container'
        });
    });
</script>
<br>
<div class="grid grid-cols-12 space-x-4">
    {#if paths}
    <select class="select col-start-3 col-end-6" bind:value={curr_path}>
        {#each paths as spec}
        <option value={spec[0]}>{spec[0]}</option>
        {/each}
    </select>
    {/if}
<button class="btn variant-ringed" on:click={async () => {
    const response = await fetch('/api/my/base/openAPI/delete?action=' + curr_path, {
        method: "DELETE",
        headers: {"Authorization": "Bearer " + $user.JWT}
    })
    if (response.ok) {
        alert("openapi spec succesfully deleted!");
        
    } else {
        alert("Something went wrong while deleting this spec");
    }
}}>delete</button>
<button class="btn variant-ringed">edit</button>
</div>
<div id="swagger-ui-container" />