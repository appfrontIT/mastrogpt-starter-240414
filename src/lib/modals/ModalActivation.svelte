<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';

	export let parent: SvelteComponent;

	const modalStore = getModalStore();
    const cButton = 'fixed top-4 right-4 z-50 font-bold shadow-xl';
	const cBase = 'w-screen h-screen';
</script>

{#if $modalStore[0]}
<div class="modal-example-fullscreen {cBase}">
    <div class="card p-4 my-2 mx-48 leading-relaxed">
        <div class="flex">
            <p class="font-bold ">Activation ID:</p><p>&nbsp;{$modalStore[0].meta.info.activationId}</p>
        </div>
        <div class="flex">
            <p class="font-bold">Name:</p><p>&nbsp;{$modalStore[0].meta.info.name}</p>
        </div>
        <div class="flex">
            <p class="font-bold">Namespace:</p><p>&nbsp;{$modalStore[0].meta.info.namespace}</p>
        </div>
        <div class="flex">
            <p class="font-bold">Start:</p><p>&nbsp;{new Date($modalStore[0].meta.info.start).toLocaleString()}</p>
        </div>  
        <div class="flex">
            <p class="font-bold">End:</p><p>&nbsp;{new Date($modalStore[0].meta.info.end).toLocaleString()}</p>
        </div>
        <div class="flex">
            <p class="font-bold">Duration:</p><p>&nbsp;{$modalStore[0].meta.info.duration}</p>
        </div>
    </div>
    <div class="card p-4 my-2 mx-48 leading-relaxed">
        <div class="leading-relaxed flex">
            <p class="font-bold">Status:</p><p>&nbsp;{$modalStore[0].meta.info.response.status}</p>
        </div>
        <p class="font-bold">Result:</p>
        <div class="card p-4 my-2 mx-2 max-w-fit leading-relaxed">
            <pre><span>{JSON.stringify($modalStore[0].meta.info.response.result, null, 2)}</span></pre>
        </div>
    </div>
    <div class="card p-4 mx-48 my-2 leading-relaxed">
        <p class="h4 font-bold leading-relaxed">Logs</p>
        <pre><span>{JSON.stringify($modalStore[0].meta.info.logs, null, 2)}</span></pre>
    </div>
    <div class="card p-4 mx-48 my-2 leading-relaxed">
        <p class="h4 font-bold leading-relaxed">Annotations</p>
        {#each $modalStore[0].meta.info.annotations as ann}
            <div class="flex"><p class="font-bold">{ann['key']}:</p>
            {#if ann['key'] == 'limits'}    
                <pre><p> {JSON.stringify(ann['value'], null, 2)}</p></pre>
            {:else}
                <p>&nbsp;{ann['value']}</p>
            {/if}
            </div>
        {/each}
    </div>
    <br>
    <button class="btn-icon variant-filled {cButton}" on:click={parent.onClose}>×</button>
</div>
{/if}