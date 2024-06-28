<script lang="ts">
    import { popup } from '@skeletonlabs/skeleton';
    import type { PopupSettings } from '@skeletonlabs/skeleton';
    import { user, chat_room, selector, getCurrentTimestamp } from "../store";
    import { onMount } from "svelte";
    import { AppBar } from '@skeletonlabs/skeleton';
    import { getModalStore } from '@skeletonlabs/skeleton';
    import TemplateCarousel from './TemplateCarousel.svelte';

    const modalStore = getModalStore();

    let actions = new Array();
    let primaryColor: any = -1;
    let secondaryColor: any = -1;
    let tertiaryColor: any = -1;
    let name: string = '';
    let description: string = '';
    let header_check: Boolean = false;
    let header_description: string = '';
    let footer_check: Boolean = false;
    let footer_description: string = '';
    let action_arr = new Array();
    let n_cols: number = -1;
    let n_rows: number = -1;
    let cols_description: string = '';
    let rows_description: string = '';

    onMount(async () => {
		actions = await get_actions();
        console.log(actions)
    })

    async function get_actions() {
		const response = await fetch('api/my/base/action/find_all', {
			method: 'GET',
			headers: {"Authorization": "Bearer " + $user!['JWT']}
		})
		if (response.status != 200) {
			return null
		}
		return await response.json();
	}

    function add_action(i: number) {
        if (actions && !action_arr.includes(actions[i])) {
            action_arr.push(actions[i]);
            action_arr = action_arr;
        }
    }
    function rm_action(i: number) {
        if (actions && action_arr.includes(actions[i])) {
            const index = action_arr.indexOf(actions[i]);
            if (index > -1) {
                action_arr.splice(index, 1);
                action_arr = action_arr;
            }
        }
    }

    async function proceed() {
        if (name == '') { alert('Il campo "nome" non puó essere vuoto'); return;}
        modalStore.trigger({
            type: 'component',
            component: 'modalWaiting',
            meta: { msg: "Building your page..." }
        });
        let query: string = 'user the following informations to generate an html page (call the html_gen function):\n';
        if (primaryColor != -1) {query += `- Primary color: ${primaryColor}\n`;}
        if (secondaryColor != -1) {query += `- Secondary color: ${secondaryColor}\n`;}
        if (tertiaryColor != -1) {query += `- Tertiary color: ${tertiaryColor}\n`;}
        if (description != '') { query += `- Description: ${description}\n`}
        if (header_check && header_description != '') { query += `- Include the following page header: ${header_description}\n`}
        if (footer_check && footer_description != '') { query += `- Include the following page footer: ${footer_description}\n`}
        if (n_cols >= 1) {
            query += `- Page coloumns: ${n_cols}\n`;
            if (cols_description != '') {
                query += `- Coloumns description: ${cols_description}\n`
            }
        }
        if (n_rows >= 1) {
            query += `- Page rows: ${n_rows}\n`;
            if (rows_description != '') {
                query += `- Rows description: ${rows_description}\n`
            }
        }
        if (action_arr.length > 0) {
            query += `- Include the following actions:\n`;
            for (let i = 0; i < action_arr.length; i++) {
                query += `\t- Action:\n\t\t- name: ${action_arr[i].name}\n\t\t- package: ${action_arr[i].package}\n\t\t- url: ${action_arr[i].url}`
                const annotations = action_arr[i].annotations;
                console.log(annotations)
                for (let j = 0; j < annotations.length; j++) {
                    if (annotations[j].key === 'description') { query += `\n\t\t- description: ${annotations[j].value}`; }
                    else if (annotations[j].key === 'return') { query += `\n\t\t- returns: ${annotations[j].value}`; }
                }
            }
        }
        $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': query}]
        const data = JSON.stringify({'input': $chat_room[$selector].history, 'name': name, 'id': $user!['_id']});
        const response = await fetch($chat_room[$selector].url, {
			method: 'POST',
			body: data,
			headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + $user!['JWT']}
		})
        $chat_room[$selector].messageFeed = new Array({
			host: false,
			name: 'Hari',
			timestamp: `Today @ ${getCurrentTimestamp()}`,
			message: `Ho generato la pagina che mi hai richiesto, se posso aiutarti con altro fammi sapere`,
			color: 'variant-soft-primary'
		})
        modalStore.close();
        $chat_room[$selector].showEditor = true;
    }

</script>
<div>
<AppBar background="0x44000000">
    <TemplateCarousel />
</AppBar>
<div class="flex gap-2 input-group input-group-divider">
	<div class="input-group-shim">Primary</div><input class="input flex-none w-14" type="color" bind:value={primaryColor} />
	<input class="input flex-none w-36" type="text" bind:value={primaryColor} readonly tabindex="-1" />
    <div class="input-group-shim">Secondary</div><input class="input flex-none w-14" type="color" bind:value={secondaryColor} />
	<input class="input flex-none w-36" type="text" bind:value={secondaryColor} readonly tabindex="-1" />
    <div class="input-group-shim">Tertiary</div><input class="input flex-none w-14" type="color" bind:value={tertiaryColor} />
	<input class="input flex-none w-36" type="text" bind:value={tertiaryColor} readonly tabindex="-1" />
</div>
<br>
<p>Name</p>
<div class="input-group input-group-divider grid-cols-[auto_1fr_auto]">
  <div class="input-group-shim">{$user.username}/</div>
  <input type="text" placeholder="https://nuvolaris.dev/api/v1/web/gporchia/display/..." bind:value={name}/>
</div>
<br>
<p>Description</p>
<textarea class="textarea" rows="4" placeholder="Enter a description to pass to the AI to generate your UI" bind:value={description}/>
<div class="space-y-2">Layout<br>
    <div class="space-y-2">
        <label class="flex items-center space-x-2">
            <input class="checkbox" type="checkbox" bind:value={header_check}/>
            <p>Header</p>
            <input class="input" title="header description" type="text" placeholder="header description" bind:value={header_description}/>
            <input class="checkbox" type="checkbox" bind:value={footer_check}/>
            <p>Footer</p>
            <input class="input" title="footer description" type="text" placeholder="footer description" bind:value={footer_description}/>
        </label>
    </div>
	<div class="input-group input-group-divider flex">
		<div class="input-group-shim flex-none w-40">Number of cols</div>
		<input title="number of cols" type="number" placeholder="n cols" bind:value={n_cols}/>
        <div class="input-group-shim">description</div>
		<input class="flex-auto" title="description" type="text" placeholder="cols description" bind:value={cols_description}/>
    </div>
    <div class="input-group input-group-divider flex">
		<div class="input-group-shim flex-none w-40">Number of rows</div>
		<input title="number of rows" type="number" placeholder="n rows" bind:value={n_rows}/>
        <div class="input-group-shim">description</div>
		<input class="flex-auto" title="description" type="text" placeholder="rows description" bind:value={rows_description}/>
    </div>
</div>
<br>
<p>Actions</p>
<div>
    <div class="grid grid-cols-6">
        {#each actions as action, i}
        {#if $user && $user['package'].includes(action.package)}
        <div class="input-group input-group-divider grid-cols-[auto_1fr_auto] rounded-container-token col-span-3">
            <button class="input-group-shim" use:popup={{event: 'click', target: 'action-' + i, placement: 'top'}}>?</button>
            <p>{action.name}</p>
            {#if action_arr.includes(action)}
                <button class='variant-filled-primary' on:click={() => {rm_action(i)}} id="action_{i}">-</button>
            {:else}
                <button class='input-group-shim' on:click={() => {add_action(i)}} id="action_{i}">+</button>
            {/if}
        </div>
        <div class="card p-4 w-72 shadow-xl" data-popup="action-{i}">
            {#each action.annotations as ann}
            {#if ann.key === 'description'}
                {ann.value}
            {/if}
            {/each}
        </div>
        {/if}
        {/each}
    </div>
</div>
</div>