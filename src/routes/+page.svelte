<script lang="ts">
	import manual_svg from '$lib/assets/manual.svg';
	import code_svg from '$lib/assets/coding.svg';
	import admin_svg from '$lib/assets/admin.svg';
	import Editor from '$lib/Editor.svelte';
	import Admin from '$lib/Admin.svelte';
	import Website from '$lib/Website.svelte';
	import website_svg from '$lib/assets/website.svg';
	import chart_svg from '$lib/assets/chart.svg';
	import { onMount, onDestroy } from 'svelte';
	import { getDrawerStore, type DrawerSettings } from '@skeletonlabs/skeleton';
	import { Avatar, AppBar, Drawer, ProgressBar, ProgressRadial, popup, Toast, } from '@skeletonlabs/skeleton';
	import type { PopupSettings } from '@skeletonlabs/skeleton';
	import { chat_room, selector, user, editor, logged } from '../store';
	import Chart from '$lib/Chart.svelte';
	import AppRail from '$lib/AppRail.svelte';
	import Chat from '$lib/Chat.svelte';
	import Flow from '$lib/flow/Flow.svelte';
	import { SvelteFlowProvider } from '@xyflow/svelte';

	const drawerStore = getDrawerStore();

	const popupFeatured: PopupSettings = {
		event: 'click',
		target: 'popupFeatured',
		placement: 'bottom',
	};

	let loading_msg = false;
	let manPage = 'https://appfront-operations.gitbook.io/lookinglass-manuale-utente';
	let reader;

	onMount(async () => {
		reader = new FileReader()
		loading_msg = false;
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
	});

	function lookinglass() { $selector = 1; drawerStore.close();}
	function coder() { $selector = 2; drawerStore.close();}
	function admin() { $selector = 3; drawerStore.close();}
	function website() { $selector = 4; drawerStore.close();}
	function chart() { $selector = 5; drawerStore.close();}

</script>
<div class="grid grid-cols-[auto_2fr]" style="height: 87vh;">
<AppRail />
	<div class="grid grid-cols-subgrid max-h-[87vh] space-y-2">
		<div class="grid grid-cols-2">
		{#if $selector === 1}
		<Chat />
		<object title="appfront-page" type="text/html" data={manPage} class="h-full w-full"/>
		{:else if $selector === 2}
		<Chat />
		<Editor />
		{:else if $selector === 3}
			<Admin />
		{:else if $selector === 4}
		{#if $chat_room[$selector].showEditor}
		<Chat />
		<Editor />
		{:else}
		<Website />
		{/if}
		{:else if $selector === 5}
		{#if $chat_room[$selector].showEditor}
		<Chat />
		<Editor />
		{:else}
		<Chat />
		<Chart />
		{/if}
		{:else if $selector === 6}
		<div class="col-span-2">
			<SvelteFlowProvider>
				<Flow />
			</SvelteFlowProvider>
		</div>
		{:else if $selector === 0}
		<Chat />
		<object title="appfront-page" type="text/html" data="https://www.appfront.cloud/walkiria" class="h-full w-full"/>
		{/if}
	</div>
	</div>
</div>

<Drawer>
	<dl class="list-dl">
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={lookinglass}><img alt="manual img" src={manual_svg} width="300" height="300"/></button>
			<span class="flex-auto">
				<dt>Lookinglass</dt>
				<dd>Do you need any information about Lookinglass procedures? Do you forgot how to make something? You can't find a page inside the Lookinglass manual? Than talk with me!</dd>
			</span>
		</div>
		<br>
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={coder}><img alt="coder img" src={code_svg} width="200" height="200"/></button>
			<span class="flex-auto">
				<dt>Coder</dt>
				<dd>Do you want to develop some action? Or add functionalities to your application? Talk with, I'm a professional developer!</dd>
			</span>
		</div>
		<br>
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={admin}><img alt="admin img" src={admin_svg} width="140" height="140"/></button>
			<span class="flex-auto">
				<dt>Admin</dt>
				<dd>I'm here to assist you into delicate task about administration and management</dd>
			</span>
		</div>
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={website}><img alt="website img" src={website_svg} width="140" height="140"/></button>
			<span class="flex-auto">
				<dt>Website</dt>
				<dd>I will guide you step by step on how to build a small working interface to incorporate your actions!</dd>
			</span>
		</div>
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={chart}><img alt="website img" src={chart_svg} width="140" height="140"/></button>
			<span class="flex-auto">
				<dt>Chart</dt>
				<dd>Wanna build awsome charts to display any kind of data? I'm the right person for you!</dd>
			</span>
		</div>
	</dl>
</Drawer>
