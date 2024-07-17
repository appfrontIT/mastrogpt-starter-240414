<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';

	export let parent: SvelteComponent;

	const modalStore = getModalStore();
    const cButton = 'fixed top-4 right-4 z-50 font-bold shadow-xl';
	const cBase = 'bg-surface-100-800-token w-screen h-screen p-4 flex overflow-y-auto overflow-x-auto';
</script>

{#if $modalStore[0]}
	<div class="modal-example-fullscreen {cBase}">
        <div class="flex flex-col space-y-4">
            <pre>
                <p class="h2">{$modalStore[0].meta.title}</p>
                {$modalStore[0].meta.msg}
            </pre>
        </div>
	</div>
    <button class="btn-icon variant-filled {cButton}" on:click={parent.onClose}>×</button>
{/if}