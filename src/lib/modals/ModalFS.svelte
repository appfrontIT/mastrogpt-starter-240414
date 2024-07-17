<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';
    import EditorFS from '../EditorFS.svelte';

	export let parent: SvelteComponent;

	const modalStore = getModalStore();

	const cBase = 'bg-surface-100-800-token w-screen h-screen p-4 flex justify-center items-center';
</script>

{#if $modalStore[0]}
	<div class="modal-example-fullscreen {cBase}">
		<div class="basis-full h-full items-center space-y-4">
			<EditorFS bind:parent/>
		</div>
	</div>
{/if}