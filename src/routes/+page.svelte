{#await promise then us}
<AppBar>
	<svelte:fragment slot="lead">
		<h1 class="h1 font-bold"><span class="bg-gradient-to-br from-pink-500 to-violet-500 bg-clip-text text-transparent box-decoration-clone">Walkiria</span></h1>
	</svelte:fragment>
	<svelte:fragment slot="trail">
		<ol class="breadcrumb">
			<!-- <li class="crumb"><a class="anchor" href="/elements/breadcrumbs">docs</a></li> -->
			<li class="crumb-separator" aria-hidden><span class="divider-vertical h-10" /></li>
			<li class="crumb"><a class="anchor" href="/swagger-ui">swagger</a></li>
			<li class="crumb-separator" aria-hidden><span class="divider-vertical h-10" /></li>
			<li use:popup={popupFeatured}><Avatar
				initials={us.username[0]}
				border="border-4 border-surface-300-600-token hover:!border-primary-500"
				cursor="cursor-pointer"
			/></li>
			<div class="card p-4 w-72 shadow-xl" data-popup="popupFeatured">
				<div><button class="btn" on:click={logout}>Logout</button></div>
				<!-- <div><button class="btn" on:click={swagger}>Swagger</button></div> -->
				<div class="arrow bg-surface-100-800-token" />
			</div>
		</ol>
	</svelte:fragment>
</AppBar>
<div class="chat grid grid-cols-7 gap-3 space-y-2" style="height: 87vh;">
	<div class="grid grid-rows-[1fr_auto] gap-1 col-span-3">
		<section bind:this={elemChat} class="max-h-[80vh] p-4 overflow-y-auto space-y-4 col-span-3">
			<div class="grid row-span-1 col-span-3 input-group input-group-divider grid-cols-[auto_1fr_auto]">
				<button class="btn-sm variant-filled input-group-shim" on:click={trigger}>chatbot</button>
				<div>
					{#if $selector == 0} Lookinglass
					{:else if $selector == 1} Coder
					{:else if $selector == 2} Admin
					{:else} Select your chat bot!
					{/if}
				</div>
			</div>
			{#if $selector != -1}
			{#each $chat_room[$selector].messageFeed as bubble}
				{#if bubble.host === false}
					<div class="grid grid-cols-[auto_1fr] gap-2">
						<Avatar src={hari} width="w-12" />
						<div class="card p-4 variant-soft rounded-tl-none space-y-4">
							<header class="flex justify-between items-center">
								<p class="font-bold">Hari</p>
								<small class="opacity-50">{bubble.timestamp}</small>
							</header>
							<p>{bubble.message}</p>
						</div>
					</div>
				{:else}
					<div class="grid grid-cols-[1fr_auto] gap-2">
						<div class="card p-4 rounded-tr-none space-y-4 {bubble.color}">
							<header class="flex justify-between items-center">
								<p class="font-bold">{us.username}</p>
								<small class="opacity-50">{bubble.timestamp}</small>
							</header>
							<p>{bubble.message}</p>
						</div>
						<Avatar initials={us.username[0]} width="w-12" />
					</div>
				{/if}
			{/each}
			{#if loading_msg === true}
				<ProgressRadial width="w-20"/>
			{/if}
			{/if}
		</section>
		<!-- Prompt -->
		<div class="input-group input-group-divider grid-cols-[auto_1fr_auto] rounded-container-token col-span-3">
			<button class="input-group-shim" on:click={new_chat}>+</button>
			<textarea
				bind:value={currentMessage}
				class="bg-transparent border-0 ring-0"
				name="prompt"
				id="prompt"
				placeholder="Write a message..."
				rows="1"
				on:keydown={onPromptKeydown}
			/>
			<button class={currentMessage ? 'variant-filled-primary' : 'input-group-shim'} on:click={addMessage}>
				send
			</button>
		</div>
	</div>
	<!-- Right column -->
	<div class="col-span-4 h-full space-y-2" id="right_div">
		{#if $selector === 0}
			<object title="appfront-page" type="text/html" data={manPage} class="h-full w-full"/>
		{:else if $selector === 1}
			<Editor />
		{:else if $selector === 2}
			<Admin />
		{:else if $selector === 3}
			<Website />
		{:else}
			<object title="appfront-page" type="text/html" data="https://www.appfront.cloud/walkiria" class="h-full w-full"/>
		{/if}
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
	</dl>
</Drawer>
{:catch}
	{logout()}
{/await}
<script lang="ts">
	import hari from '$lib/hari.png'
	import manual_svg from '$lib/manual.svg'
	import code_svg from '$lib/coding.svg'
	import admin_svg from '$lib/admin.svg'
	import Editor from '$lib/Editor.svelte';
	import Admin from '$lib/Admin.svelte'
	import Website from '$lib/Website.svelte';
	import website_svg from '$lib/website.svg'
	import { Avatar } from '@skeletonlabs/skeleton';
	import { AppBar } from '@skeletonlabs/skeleton';
	import { onMount, onDestroy } from 'svelte';
	import { Drawer } from '@skeletonlabs/skeleton';
	import { ProgressBar } from '@skeletonlabs/skeleton';
	import { ProgressRadial } from '@skeletonlabs/skeleton';
	import { getDrawerStore, type DrawerSettings } from '@skeletonlabs/skeleton';
	import { popup } from '@skeletonlabs/skeleton';
	import type { PopupSettings } from '@skeletonlabs/skeleton';
	import { chat_room, selector, user, editor } from '../store'
	
	const drawerStore = getDrawerStore();

	const popupFeatured: PopupSettings = {
		event: 'click',
		target: 'popupFeatured',
		placement: 'bottom',
	};

	let currentMessage = '';
	let elemChat: HTMLElement;
	let loading_msg = false;
	let promise = get_user();
	let manPage = 'https://appfront-operations.gitbook.io/lookinglass-manuale-utente';

	async function get_user() {
		const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })

		if (res.ok) { const obj = await res.json(); $user = obj; return obj; }
		else { throw new Error('failed to get user') };
	}

	const interval = setInterval(async () => {
		const r = await fetch('api/my/db/chat', {
			credentials: 'include'
		})
		if (r.status === 200) {
			const obj = await r.json();
			for (let i = 0; i < obj.length; i++) {
				if ('editor' in obj[i]) {
					$editor = obj[i].editor
				} else {
					if('frame' in obj[i]) { manPage = obj[i].frame }
					const newMessage = {
						host: false,
						timestamp: `Today @ ${getCurrentTimestamp()}`,
						message: obj[i].output,
						color: 'variant-soft-primary'
					};
					$chat_room[$selector].messageFeed = [...$chat_room[$selector].messageFeed, newMessage];
					$chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'assistant', 'content': obj[i].output}]
					setTimeout(() => { scrollChatBottom('smooth'); }, 0);
				}
			}
			loading_msg = false;
		}
	}, 2000)
	
	function scrollChatBottom(behavior?: ScrollBehavior): void {
		if (elemChat)
			elemChat.scrollTo({ top: elemChat.scrollHeight, behavior });
		else
			setTimeout(() => { scrollChatBottom('smooth'); }, 0);
	}

	function getCurrentTimestamp(): string {
		const date = new Date().toLocaleString('en-GB', { hour: 'numeric', minute: 'numeric', hour12: true });
		return date;
	}

	async function addMessage(): Promise<void> {
		const newMessage = {
			host: true,
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: currentMessage,
			color: 'variant-soft-primary'
		};
		$chat_room[$selector].messageFeed = [...$chat_room[$selector].messageFeed, newMessage];
		$chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': currentMessage}]
		const data = JSON.stringify({'input': $chat_room[$selector].history});
		currentMessage = '';
		setTimeout(() => { scrollChatBottom('smooth'); }, 0);
		loading_msg = true;
		const response = await fetch($chat_room[$selector].url, {
			method: 'POST',
			body: data,
			headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + $user['JWT']}
		})
	}

	function onPromptKeydown(event: KeyboardEvent): void {
		if (['Enter'].includes(event.code)) {
			event.preventDefault();
			addMessage();
		}
	}

	onMount(async () => {
		scrollChatBottom();
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
	});
	
	onDestroy(() => clearInterval(interval));

	function lookinglass() { $selector = 0;}
	function coder() { $selector = 1;}
	function admin() { $selector = 2;}
	function website() { $selector = 3;}

	function trigger() {
		const drawerSettings: DrawerSettings = {
			// Provide your property overrides:
			bgDrawer: 'bg-purple-900 text-white',
			bgBackdrop: 'bg-gradient-to-tr from-indigo-500/50 via-purple-500/50 to-pink-500/50',
			width: 'w-[280px] md:w-[480px]',
			padding: 'p-4',
			rounded: 'rounded-xl',
		};
		drawerStore.open(drawerSettings);
	}

	async function logout() {
		const response = await fetch('api/my/base/auth/logout', {
			method: 'DELETE',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json'},
		});
		$user = null;
		document.cookie = 'appfront-sess-cookie=;expires=Thu, 01 Jan 1970 00:00:01 GMT'
        sessionStorage.clear()
        return window.parent.location.replace('/login')
	}

	function new_chat() {
		$chat_room[$selector].history = new Array();
		$chat_room[$selector].messageFeed = new Array();
	}

	function swagger() {
		return window.location.assign('/swagger-ui')
	}

</script>