<script lang="ts">
	import '../app.postcss';

	// Highlight JS
	import hljs from 'highlight.js/lib/core';
	import 'highlight.js/styles/github-dark.css';
	import { storeHighlightJs } from '@skeletonlabs/skeleton';
	import xml from 'highlight.js/lib/languages/xml'; // for HTML
	import css from 'highlight.js/lib/languages/css';
	import javascript from 'highlight.js/lib/languages/javascript';
	import typescript from 'highlight.js/lib/languages/typescript';
	import { initializeStores, Drawer, Modal, Toast, type ModalComponent } from '@skeletonlabs/skeleton';
	import ModalWaiting from '$lib/ModalWaiting.svelte';
	import ModalFs from '$lib/ModalFS.svelte';
	import ModalConfirm from '$lib/ModalConfirm.svelte';
	import ModalData from "$lib/ModalData.svelte";
	import Header from '$lib/Header.svelte';
	import { logged } from '../store';

	const modalRegistry: Record<string, ModalComponent> = {
		modalWaiting: { ref: ModalWaiting },
		modalFs: { ref: ModalFs },
		modalConfirm: { ref: ModalConfirm },
		modalData: { ref: ModalData }
	};

	initializeStores();

	hljs.registerLanguage('xml', xml); // for HTML
	hljs.registerLanguage('css', css);
	hljs.registerLanguage('javascript', javascript);
	hljs.registerLanguage('typescript', typescript);
	storeHighlightJs.set(hljs);

	// Floating UI for Popups
	import { computePosition, autoUpdate, flip, shift, offset, arrow } from '@floating-ui/dom';
	import { storePopup } from '@skeletonlabs/skeleton';
	storePopup.set({ computePosition, autoUpdate, flip, shift, offset, arrow });
</script>
{#if $logged}
	<Header />
{/if}
<Toast />
<Modal components={modalRegistry} />
<slot />
