<script lang="ts">
    import { onMount } from 'svelte';
    import * as swaggerJson from '../../lib/appfront.json';
    import SwaggerUI from 'swagger-ui';
    import 'swagger-ui/dist/swagger-ui.css';
    import { user } from '../../store'
    onMount(async () => {
        SwaggerUI({
            spec: swaggerJson,
            dom_id: '#swagger-ui-container'
        });
    });
</script>

<div id="swagger-ui-container" />