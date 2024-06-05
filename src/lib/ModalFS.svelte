<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';
    import Editor from './Editor.svelte';

	export let parent: SvelteComponent;

	const modalStore = getModalStore();

	const cBase = 'bg-surface-100-800-token w-screen h-screen p-4 flex justify-center items-center';
</script>

{#if $modalStore[0]}
	<div class="modal-example-fullscreen {cBase}">
		<div class="flex flex-col items-center space-y-4">
			<h2 class="h2">Full Screen Modal</h2>
			<p>This demonstrates a full screen modal dialog.</p>
			<button class="btn variant-filled" on:click={parent.onClose}>× Close</button>
		</div>
	</div>
{/if}