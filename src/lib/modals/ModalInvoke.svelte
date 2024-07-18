<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';
	import { user } from '../../store';

	export let parent: SvelteComponent;
    let headers = []
    let parameters = []
    let path: string = '';
    let method: string = "GET";

	const modalStore = getModalStore();
    const cButton = 'fixed top-4 right-4 z-50 font-bold shadow-xl';
	const cBase = 'bg-surface-100-800-token card p-4 verflow-y-auto overflow-x-auto overflow-y-auto w-1/3 h-2/3 max-h-screen';
</script>

{#if $modalStore[0]}
	<div class="modal-example-fullscreen {cBase} text-xl">
        <div>
            <span class="label">Path</span>
            <input class="input rounded-sm text-base" bind:value={path} placeholder="path" />
            <span class="label">Method</span>
            <input class="input rounded-sm text-base" bind:value={method} placeholder="path" />
            <span class="label">Headers</span>
            <div class="grid grid-cols-3">
            {#each headers as v, i}
                <input class="input rounded-sm text-base" id={i} type="text" bind:value={headers[i].key} placeholder="key"/>
                <input class="input rounded-sm text-base col-span-2" id={i} type="text" bind:value={headers[i].value} placeholder="value"/>
            {/each}
            </div>
            <div class="text-center">
            <button class="btn rounded-sm text-base" on:click|preventDefault={() => {
                headers = [...headers, {key: '', value: ''}]
            }}>Add</button><span class="divider-vertical h-4" />
            <button class="btn rounded-sm text-base" on:click={() => {
                if (headers.length == 1) { return ;}
                headers = headers.slice(0, headers.length - 1);
            }}>Remove</button>
            </div>
        </div>
        <div>
            <span class="label">Parameters</span>
            <div class="grid grid-cols-3">
                {#each parameters as v, i}
                    <input class="input rounded-sm text-base" id={i} type="text" bind:value={parameters[i].key} placeholder="key"/>
                    <input class="input rounded-sm text-base col-span-2" id={i} type="text" bind:value={parameters[i].value} placeholder="value"/>
                {/each}
            </div>
            <div class="text-center">
            <button class="btn rounded-sm text-base" on:click|preventDefault={() => {
                parameters = [...parameters, {key: '', value: ''}]
            }}>Add</button><span class="divider-vertical h-4" />
            <button class="btn rounded-sm text-base" on:click={() => {
                if (parameters.length == 1) { return ;}
                parameters = parameters.slice(0, parameters.length - 1);
            }}>Remove</button>
            </div>
        </div>
        <div class="text-center">
            <button class="btn variant-filled" on:click={async() => {
                let set_headers = {};
                for (let i = 0; i < headers.length; i++) {
                    set_headers[headers[i].key] = headers[i].value;
                }
                set_headers['Authorization'] = "Bearer " + $user.JWT;
                let set_parameters = null;
                for (let i = 0; i < parameters.length; i++) {
                    set_parameters[parameters[i].key] = parameters[i].value;
                }
                if (path.length > 0) { path = "/" + path; }
                if (set_parameters) {
                    const response = await fetch('api/my'+ $modalStore[0].meta.action.url.split('mcipolla')[1] + path, {
                        method: method.toUpperCase(),
                        headers: set_headers,
                        credentials: 'include',
                        body: JSON.stringify(set_parameters)
                    })
                    console.log(response.status);
                } else {
                    const response = await fetch('api/my'+ $modalStore[0].meta.action.url.split('mcipolla')[1] + path, {
                        method: method.toUpperCase(),
                        headers: set_headers,
                        credentials: 'include',
                    })
                    console.log(response.status);
                }
            }}>send</button>
        </div>
    </div>
    <button class="btn-icon variant-filled {cButton}" on:click={parent.onClose}>×</button>
{/if}