<AppBar>
	<svelte:fragment slot="lead">
		<h1 class="h1 font-bold"><span class="bg-gradient-to-br from-pink-500 to-violet-500 bg-clip-text text-transparent box-decoration-clone">Walkiria</span></h1>
	</svelte:fragment>
	<svelte:fragment slot="trail">
		<ol class="breadcrumb">
			<li class="crumb"><a class="anchor" href="/elements/breadcrumbs">docs</a></li>
			<li class="crumb-separator" aria-hidden><span class="divider-vertical h-10" /></li>
			<li class="crumb"><a class="anchor" href="/elements/breadcrumbs">actions</a></li>
			<li class="crumb-separator" aria-hidden><span class="divider-vertical h-10" /></li>
			<li><Avatar
				initials="JD"
				border="border-4 border-surface-300-600-token hover:!border-primary-500"
				cursor="cursor-pointer"
			/></li>
		</ol>
	</svelte:fragment>
</AppBar>
<div class="chat w-full grid grid-cols-7 gap-3 space-y-2" style="height: 87vh;">
	<div class="grid grid-rows-[1fr_auto] gap-1 col-span-3">
		<section bind:this={elemChat} class="max-h-[80vh] p-4 overflow-y-auto space-y-4 col-span-3">
			{#each messageFeed as bubble}
				{#if bubble.host === false}
					<div class="grid grid-cols-[auto_1fr] gap-2">
						<Avatar src={hari} width="w-12" />
						<div class="card p-4 variant-soft rounded-tl-none space-y-4">
							<header class="flex justify-between items-center">
								<p class="font-bold">{bubble.name}</p>
								<small class="opacity-50">{bubble.timestamp}</small>
							</header>
							<p>{bubble.message}</p>
						</div>
					</div>
				{:else}
					<div class="grid grid-cols-[1fr_auto] gap-2">
						<div class="card p-4 rounded-tr-none space-y-4 {bubble.color}">
							<header class="flex justify-between items-center">
								<p class="font-bold">{bubble.name}</p>
								<small class="opacity-50">{bubble.timestamp}</small>
							</header>
							<p>{bubble.message}</p>
						</div>
						<Avatar initials="JD" width="w-12" />
					</div>
				{/if}
			{/each}
		</section>
		<!-- Prompt -->
		<div class="input-group input-group-divider grid-cols-[auto_1fr_auto] rounded-container-token col-span-3">
			<button class="input-group-shim" on:click={trigger}>+</button>
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
		{#if selector === 1}
		<object title="appfront-page" type="text/html" data="https://appfront-operations.gitbook.io/lookinglass-manuale-utente" class="h-full w-full"/>
		{:else if selector === 2}
			<Editor />
		{:else if selector === 3}
			<div></div>
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
			<button type="button" on:click={coder}><img alt="manual img" src={code_svg} width="200" height="200"/></button>
			<span class="flex-auto">
				<dt>Coder</dt>
				<dd>Do you want to develop some action? Or add functionalities to your application? Talk with, I'm a professional developer!</dd>
			</span>
		</div>
		<br>
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={admin}><img alt="manual img" src={admin_svg} width="140" height="140"/></button>
			<span class="flex-auto">
				<dt>Admin</dt>
				<dd>I'm here to assist you into delicate task about administration and management</dd>
			</span>
		</div>
	</dl>
</Drawer>
<script lang="ts">
	import hari from '$lib/hari.png'
	import walkiria_logo from '$lib/appfront_logo.png'
	import manual_svg from '$lib/manual.svg'
	import code_svg from '$lib/coding.svg'
	import admin_svg from '$lib/admin.svg'
	import Editor from '../components/Editor.svelte';
	import { Avatar } from '@skeletonlabs/skeleton';
	import { AppBar } from '@skeletonlabs/skeleton';
	import { onMount } from 'svelte';
	import { Drawer } from '@skeletonlabs/skeleton';
	import { getDrawerStore, type DrawerSettings } from '@skeletonlabs/skeleton';
	const drawerStore = getDrawerStore();

	let messageFeed: string | any[] = [];
	let currentMessage = '';
	let elemChat: HTMLElement;
	let open = false;
	let selector: number = 0;

	function scrollChatBottom(behavior?: ScrollBehavior): void {
		elemChat.scrollTo({ top: elemChat.scrollHeight, behavior });
	}

	function getCurrentTimestamp(): string {
		return new Date().toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
	}

	function addMessage(): void {
		const newMessage = {
			id: messageFeed.length,
			host: true,
			avatar: 48,
			name: 'Jane',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: currentMessage,
			color: 'variant-soft-primary'
		};
		// Append the new message to the message feed
		messageFeed = [...messageFeed, newMessage];
		// Clear the textarea message
		currentMessage = '';
		// Smoothly scroll to the bottom of the feed
		setTimeout(() => { scrollChatBottom('smooth'); }, 0);
	}

	function onPromptKeydown(event: KeyboardEvent): void {
		if (['Enter'].includes(event.code)) {
			event.preventDefault();
			addMessage();
		}
	}

	onMount(() => {
		scrollChatBottom();
	});

	function lookinglass() { selector = 1; }

	function coder() { selector = 2; }

	function admin() { selector = 3; }


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

</script>