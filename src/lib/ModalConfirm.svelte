<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';
    import { ProgressBar } from '@skeletonlabs/skeleton';

	export let parent: SvelteComponent;

	const modalStore = getModalStore();

	const cButton = 'fixed top-4 right-4 z-50 font-bold shadow-xl';
</script>

{#if $modalStore[0]}
	<div class="card p-4 w-modal shadow-xl space-y-4">
		<p>{$modalStore[0].meta.msg}</p>
	</div>
    <button class="btn-icon variant-filled {cButton}" on:click={parent.onClose}>×</button>
{/if}