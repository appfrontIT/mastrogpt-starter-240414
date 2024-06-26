<div class="chat grid grid-cols-7 gap-3 space-y-2" style="height: 87vh;">
	<div class="grid grid-rows-[1fr_auto] gap-1 col-span-3">
		<section bind:this={elemChat} class="max-h-[80vh] p-4 overflow-y-auto space-y-4 col-span-3">
			<div class="grid row-span-1 col-span-3 input-group input-group-divider grid-cols-[auto_1fr_auto_auto]">
				<button class="btn-sm variant-filled input-group-shim" on:click={bots_trigger}>chatbot</button>
				<div>
					{#if $selector == 0} Select your chat bot!
					{:else if $selector == 1} Lookinglass
					{:else if $selector == 2} Coder
					{:else if $selector == 3} Admin
					{:else if $selector == 4} Website
					{:else if $selector == 5} Chart
					{/if}
				</div>
				<button class={voice_on ? "variant-filled-primary" : "input-group-shim"} on:click={toggle_voice}><img alt="clip img" src={voice_on_svg} width="20" height="20"/></button>
				<button class="btn-sm input-group-shim"><img alt="clip img" src={clip_svg} width="20" height="20"/></button>
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
							<SvelteMarkdown source={bubble.message} />
						</div>
					</div>
				{:else}
					<div class="grid grid-cols-[1fr_auto] gap-2">
						<div class="card p-4 rounded-tr-none space-y-4 {bubble.color}">
							<header class="flex justify-between items-center">
								<p class="font-bold">{$user.username}</p>
								<small class="opacity-50">{bubble.timestamp}</small>
							</header>
							<p>{bubble.message}</p>
						</div>
						<Avatar initials={$user.username[0]} width="w-12" />
					</div>
				{/if}
			{/each}
			{#if loading_msg === true}
				<ProgressRadial width="w-20"/>
			{/if}
			{/if}
		</section>
		<!-- Prompt -->
		<div class="input-group input-group-divider grid-cols-[auto_1fr_auto_auto] rounded-container-token col-span-3">
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
			<button class={recording ? 'variant-filled-primary' : 'input-group-shim'} on:click={record}><img alt="record img" src={microphone_svg} width="20" height="20" /></button>
			<button class={currentMessage ? 'variant-filled-primary' : 'input-group-shim'} on:click={addMessage}>
				send
			</button>
		</div>
	</div>
	<!-- Right column -->
	<div class="col-span-4 h-full space-y-2" id="right_div">
		{#if $selector === 1}
			<object title="appfront-page" type="text/html" data={manPage} class="h-full w-full"/>
		{:else if $selector === 2}
			<Editor />
		{:else if $selector === 3}
			<Admin />
		{:else if $selector === 4}
			{#if $chat_room[$selector].showEditor}
				<Editor />
			{:else}
				<Website />
			{/if}
		{:else if $selector === 5}
			{#if $chat_room[$selector].showEditor}
				<Editor />
			{:else}
				<Chart />
			{/if}
		{:else if $selector === 0}
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
		<div class="w-full grid grid-cols-2 gap-3">
			<button type="button" on:click={chart}><img alt="website img" src={chart_svg} width="140" height="140"/></button>
			<span class="flex-auto">
				<dt>Chart</dt>
				<dd>Wanna build awsome charts to display any kind of data? I'm the right person for you!</dd>
			</span>
		</div>
	</dl>
</Drawer>

<script lang="ts">
	import SvelteMarkdown from 'svelte-markdown';
	import hari from '$lib/hari.png';
	import manual_svg from '$lib/manual.svg';
	import code_svg from '$lib/coding.svg';
	import admin_svg from '$lib/admin.svg';
	import Editor from '$lib/Editor.svelte';
	import Admin from '$lib/Admin.svelte';
	import Website from '$lib/Website.svelte';
	import website_svg from '$lib/website.svg';
	import chart_svg from '$lib/chart.svg';
	import clip_svg from '$lib/clip.svg';
	import microphone_svg from '$lib/microphone.svg'
	import voice_on_svg from '$lib/voice_on.svg'
	import { onMount, onDestroy } from 'svelte';
	import { getDrawerStore, type DrawerSettings } from '@skeletonlabs/skeleton';
	import { Avatar, AppBar, Drawer, ProgressBar, ProgressRadial, popup, Toast } from '@skeletonlabs/skeleton';
	import type { PopupSettings } from '@skeletonlabs/skeleton';
	import { chat_room, selector, user, editor, logged } from '../store';
	import Chart from '$lib/Chart.svelte';
	
	const drawerStore = getDrawerStore();

	const popupFeatured: PopupSettings = {
		event: 'click',
		target: 'popupFeatured',
		placement: 'bottom',
	};

	let recording = false;
	let voice_on = false;
	let currentMessage = '';
	let elemChat: HTMLElement;
	let loading_msg = false;
	let manPage = 'https://appfront-operations.gitbook.io/lookinglass-manuale-utente';
	let audioRecorder: MediaRecorder;
    let audioChunks = [];
	let audioCtx;

	const interval = setInterval(async () => {
		const r = await fetch('api/my/db/chat', {
			credentials: 'include'
		})
		if (r.status === 200) {
			const obj = await r.json();
			for (let i = 0; i < obj.length; i++) {
				if ('editor' in obj[i]) {
					$chat_room[$selector].editor = obj[i].editor;
				} else {
					if ('frame' in obj[i]) { manPage = obj[i].frame; }
					if ('pdf' in obj[i]) { }
					if ('showEditor' in obj[i]) { $chat_room[$selector].showEditor = obj[i].showEditor}
					if ('output' in obj[i]) {
						const newMessage = {
							host: false,
							timestamp: `Today @ ${getCurrentTimestamp()}`,
							message: obj[i].output,
							color: 'variant-soft-primary'
						};
						$chat_room[$selector].messageFeed = [...$chat_room[$selector].messageFeed, newMessage];
						$chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'assistant', 'content': obj[i].output}]
						setTimeout(() => { scrollChatBottom('smooth'); }, 0);
						if (voice_on) {
							const response = await fetch('/api/my/utility/text_to_speech', {
								method: "POST",
								body: obj[i].output
							})
							if (response.ok) {
								const data = await response.arrayBuffer();
								// console.log(data)
								// var buffer = new ArrayBuffer(data.length*2);
								// var bufferView = new Uint16Array(buffer);
								// for (let j = 0; j < data.length; j++) {
								//     bufferView[j] = data.charCodeAt(j);
								// }
								// console.log(buffer)
								const z = new Float32Array(data, 4, 4)
								const blob = new Blob([z], { type: "audio/mpeg" })
								const audioUrl = window.URL.createObjectURL(blob);
								console.log(audioUrl)
								const audio = new Audio(audioUrl);
								audio.play();
								// const decoded = await audioCtx.decodeAudioData(buffer);
								// const source = audioCtx.createBufferSource();
								// source.buffer = decoded;
								// source.connect(audioCtx.destination);
								// source.start();								
								// const audioCtx = new AudioContext();
								// const decodedData = await audioCtx.decodeAudioData(data)
								// const source = new AudioBufferSourceNode(audioCtx);
								// source.buffer = decodedData;
								// source.connect(audioCtx.destination);
								// source.start(0);
							}
						}
					}
				}
			}
			loading_msg = false;
		}
	}, 3000)
	
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
		if (currentMessage.length == 0) { return; }
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
		navigator.mediaDevices.getUserMedia({ audio: true })
		.then(stream => {
			audioRecorder = new MediaRecorder(stream);
			audioRecorder.ondataavailable = (e) => { audioChunks.push(e.data);};
			audioRecorder.onstop = async (e) => {
				const blob = new Blob(audioChunks, { type: audioRecorder.mimeType });
				
				const response  = await fetch('/api/my/utility/speech_to_text', {
					method: "POST",
					body: await blob.arrayBuffer()
				})
				if (response.ok) {
					const text = await response.text();
					currentMessage = text;
					addMessage();
				}
			}
		;})
		audioCtx = new AudioContext();
		setTimeout(() => { scrollChatBottom('smooth'); }, 0);
	});
	
	onDestroy(() => clearInterval(interval));

	function lookinglass() { $selector = 1; drawerStore.close(); setTimeout(() => { scrollChatBottom('smooth'); }, 0);}
	function coder() { $selector = 2; drawerStore.close(); setTimeout(() => { scrollChatBottom('smooth'); }, 0);}
	function admin() { $selector = 3; drawerStore.close(); setTimeout(() => { scrollChatBottom('smooth'); }, 0);}
	function website() { $selector = 4; drawerStore.close(); setTimeout(() => { scrollChatBottom('smooth'); }, 0);}
	function chart() { $selector = 5; drawerStore.close(); setTimeout(() => { scrollChatBottom('smooth'); }, 0);}

	function bots_trigger() {
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

	function new_chat() {
		$chat_room[$selector].history = new Array();
		$chat_room[$selector].messageFeed = new Array();
	}

	function record() {
		recording = recording ? false : true;
		if (recording) {
			audioChunks = [];
			audioRecorder.start();
			document.getElementById('prompt').placeholder = 'Recording...';
		} else {
			audioRecorder.stop();
			document.getElementById('prompt').placeholder = "Write a message...";
		}
	}

	function toggle_voice() { voice_on = voice_on ? false : true; }
</script>