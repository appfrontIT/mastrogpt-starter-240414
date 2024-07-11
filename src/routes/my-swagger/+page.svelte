<script lang="ts">
    import { LightSwitch } from '@skeletonlabs/skeleton';
    import { onMount } from 'svelte';
    import * as swaggerJson from '$lib/appfront.json';
    import SwaggerUI from 'swagger-ui';
    import 'swagger-ui/dist/swagger-ui.css';
    import { user, logged } from '../../store'

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
        SwaggerUI({
            spec: obj,
            dom_id: '#swagger-ui-container'
        });
    });
</script>
<br>
<div class="grid grid-cols-12 space-x-4">
<select class="select col-start-3 col-end-6">
	<option value="1">Option 1</option>
	<option value="2">Option 2</option>
	<option value="3">Option 3</option>
	<option value="4">Option 4</option>
	<option value="5">Option 5</option>
</select>
<button class="btn variant-ringed">delete</button>
<button class="btn variant-ringed">edit</button>
</div>
<div id="swagger-ui-container" />