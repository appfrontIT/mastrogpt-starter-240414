<script lang="ts">
	import SvelteMarkdown from 'svelte-markdown';
    import { selector, chat_room, user } from '../store'
    import { Avatar, ProgressRadial } from '@skeletonlabs/skeleton';
    import { getDrawerStore, type DrawerSettings } from '@skeletonlabs/skeleton';
    import hari from '$lib/hari.png'
    import clip_svg from '$lib/clip.svg';
	import microphone_svg from '$lib/microphone.svg'
	import voice_on_svg from '$lib/voice_on.svg'
	import { onMount, onDestroy } from 'svelte';
    

    const drawerStore = getDrawerStore();

    let manPage = 'https://appfront-operations.gitbook.io/lookinglass-manuale-utente';
    let filesInput;
	let recording = false;
    let elemChat: HTMLElement;
    let voice_on = false;
    let currentMessage = '';
    let loading_msg = false;
    let audioRecorder: MediaRecorder;
    let audioChunks = [];
    let audioCtx;
	let reader;

    $: $selector, setTimeout(() => { scrollChatBottom('smooth'); }, 0);

    onMount(async () => {
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
    })

    onDestroy(() => clearInterval(interval));

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
						if (voice_on) {}
					}
				}
			}
			loading_msg = false;
		}
	}, 3000)

    function onPromptKeydown(event: KeyboardEvent): void {
		if (['Enter'].includes(event.code)) {
			event.preventDefault();
			addMessage();
		}
	}

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

	async function attach_file() {
		for(let i = 0; i < filesInput.files.length; i++) {
			reader.readAsDataURL(filesInput.files[i]);
			while(reader.readyState == 1) {
				await new Promise(r => setTimeout(r, 1000));
			}
			
		}
	}
</script>

<div class="grid grid-rows-[1fr_auto] gap-1" id="chat" style="height: 87vh;">
    <section bind:this={elemChat} class="p-4 overflow-y-auto space-y-4">
        <div class="grid row-span-1 input-group input-group-divider grid-cols-[auto_1fr_auto]">
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
    <div class="grid row-span-1 input-group input-group-divider grid-cols-[auto_auto_1fr_auto_auto]">
        <button class="btn-sm input-group-shim" on:click={new_chat}>+</button>
        <input class="hidden" id="file-to-upload" type="file" accept=".png,.jpg" multiple bind:this={filesInput} on:change={attach_file}/>
        <button class="btn-sm input-group-shim" on:click={ () => filesInput.click() }><img alt="clip img" src={clip_svg} width="20" height="20"/></button>
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