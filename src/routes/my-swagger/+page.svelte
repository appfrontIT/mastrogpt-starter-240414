<script lang="ts">
    import { LightSwitch } from '@skeletonlabs/skeleton';
    import { onMount } from 'svelte';
    import * as swaggerJson from '../../lib/appfront.json';
    import SwaggerUI from 'swagger-ui';
    import 'swagger-ui/dist/swagger-ui.css';
    import { user } from '../../store'

    async function get_user() {
		const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })

		if (res.ok) { const obj = await res.json(); $user = obj; return obj; }
		else { throw new Error('failed to get user') };
	}

    onMount(async () => {
        $user = await get_user();
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
<LightSwitch />
<div id="swagger-ui-container" />