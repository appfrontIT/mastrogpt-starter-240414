<script lang="ts">
    import { user, chat_room, selector, getCurrentTimestamp } from "../store";
    import { onMount } from "svelte";
    import { popup, AppBar, getModalStore, ProgressBar } from '@skeletonlabs/skeleton';
    import Carousel from 'svelte-carousel'
	import { templates } from "../store";
    import type { ModalSettings, ModalComponent, ModalStore } from '@skeletonlabs/skeleton';

	let carousel; // for calling methods of the carousel instance
	let curr_page = 0;

    const modalStore = getModalStore();
    const modal: ModalSettings = {
        type: 'prompt',
        title: 'Action',
        body: 'Provide a description of the action in the field below.',
        value: 'Description',
        valueAttr: { type: 'text', minlength: 3, required: true },
        response: (r: string) => console.log('response:', r),
    };
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
    let steps: number = 0;
    let template = $templates[0];
    let assets =[{'img': '', 'description': ''}]

    onMount(async () => {
		actions = await get_actions();
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
        query += `You must use this webpage as example: ${template.demo}\n` 
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
        if (assets.length > 0) {
            query += `Here's a list of assets you have to use and the corrispettive descrition:`
            for (let i = 0; i < assets.length; i++) {
                query += `\nimg: ${assets[i].img}, description: ${assets[i].description}`
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

    const addField = () => {
		assets = [...assets, {img: '', description: ''}]
	};
	const removeField = () => {
		assets = assets.slice(0, assets.length-1)
	};

</script>
<div class="col-span-2 text-center space-y-4">
    {#if steps == 0}
    <div class="space-y-8">
        <p class="h2">Start by selecting your template</p>
        <div class="w-9/12 mx-auto space-x-4">
            <p class="h2">{$templates[curr_page].name}</p>
        <Carousel bind:this={carousel} on:pageChange={ event => curr_page = event.detail }>
            {#each $templates as {img, demo}, i}
                    <img
                    class="rounded-container-token hover:brightness-125"
                    src={img}
                    alt={img}
                    title={img}
                    loading="lazy"
                />
            {/each}
        </Carousel>
        <button class="btn variant-filled" on:click={() => {window.open($templates[curr_page].demo, '_blank')}}>demo</button>
        <button class="btn variant-filled" on:click={() => {template = $templates[curr_page]; steps++;}}>choose</button>
        </div>
    </div>
    {:else if steps == 1}
    <AppBar gridColumns="grid-cols-3" slotTrail="place-content-end" background="0">
        <svelte:fragment slot="lead"><button class="btn variant-filled" on:click={() => {steps--;}}>back</button></svelte:fragment>
        <p class="h2">Customize your page even more!</p>
        <svelte:fragment slot="trail"><button class="btn variant-filled" on:click={() => {steps++;}}>next</button></svelte:fragment>
    </AppBar>
    <div class="grid grid-cols-3">
        <div class="grid row-span-1 input-group input-group-divider grid-cols-[auto_auto_auto]">
            <div class="input-group-shim">Primary</div>
            <input class="input my-auto mx-auto" type="color" bind:value={primaryColor} />
            <input class="input-group-shim" type="text" bind:value={primaryColor} readonly tabindex="-1" />
        </div>
        <div class="grid row-span-1 input-group input-group-divider grid-cols-[auto_auto_auto]">
            <div class="input-group-shim">Secondary</div>
            <input class="input my-auto mx-auto" type="color" bind:value={secondaryColor} />
            <input class="input-group-shim" type="text" bind:value={secondaryColor} readonly tabindex="-1" />
        </div>
        <div class="grid row-span-1 input-group input-group-divider grid-cols-[auto_auto_auto]">
            <div class="input-group-shim">Tertiary</div>
            <input class="input my-auto mx-auto" type="color" bind:value={tertiaryColor} />
            <input class="input-group-shim" type="text" bind:value={tertiaryColor} readonly tabindex="-1" />
        </div>
</div>
<p>Name</p>
<div class="input-group input-group-divider grid-cols-[auto_1fr_auto]">
  <div class="input-group-shim">{$user.username}/</div>
  <input type="text" placeholder="https://walkiria.cloud/api/v1/web/..." bind:value={name}/>
</div>
<p>Description</p>
<textarea class="textarea" rows="8" placeholder="Enter a description to pass to the AI to generate your UI" bind:value={description}/>
<div class="space-y-4"><p>Layout</p>
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
	<!-- <div class="input-group input-group-divider flex">
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
    </div> -->
</div>
{:else if steps == 2}
<p>Actions</p>
<AppBar gridColumns="grid-cols-3" slotTrail="place-content-end" background="0">
    <svelte:fragment slot="lead"><button class="btn variant-filled" on:click={() => {steps--;}}>back</button></svelte:fragment>
    <p class="h2">Choose any action to use inside your page, or create a new one!</p>
    <svelte:fragment slot="trail"><button class="btn variant-filled" on:click={() => {steps++;}}>next</button></svelte:fragment>
</AppBar>
<div>
    {#await get_actions()}
        <p class="h5">Loading actions</p><br>
        <ProgressBar value={undefined} />
    {:then arr} 
    <div class="grid grid-cols-2">
        {#each actions as action, i}
        {#if $user && $user['package'].includes(action.package)}
        <div class="input-group input-group-divider grid-cols-[auto_1fr_auto]">
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
    {/await}
</div>
<button class="btn variant-filled" on:click={() => modalStore.trigger(modal)}>new</button>
{:else if steps == 3}
<AppBar gridColumns="grid-cols-3" slotTrail="place-content-end" background="0">
    <svelte:fragment slot="lead"><button class="btn variant-filled" on:click={() => {steps--;}}>back</button></svelte:fragment>
    <p class="h2">It's time to choose some assets for your site! Provide the asset link and description!</p>
    <svelte:fragment slot="trail"><button class="btn variant-filled" on:click={() => {steps++;}}>next</button></svelte:fragment>
</AppBar>
{#each assets as v, i}
<div class="grid grid-cols-[auto_4fr]">
	<input id={i} type="text" bind:value={assets[i].img} placeholder="image url"/>
	<input id={i} type="text" bind:value={assets[i].description} placeholder="description"/>
</div>
{/each}
<button class="btn variant-filled" on:click|preventDefault={addField}>Add</button>
<button class="btn variant-filled" on:click={removeField}>Remove</button>
{:else if steps == 4}
<AppBar gridColumns="grid-cols-3" slotTrail="place-content-end" background="0">
    <svelte:fragment slot="lead"><button class="btn variant-filled" on:click={() => {steps--;}}>back</button></svelte:fragment>
    <p class="h2">We're almost done! Here's a recap of your request:</p>
</AppBar>
<p>Name: {name}</p>
<div class="grid grid-cols-[auto_auto] space-y-4">
<p>Template:</p>
{template.name}
<p>Primary colour:</p><input class="input my-auto mx-auto" type="color" bind:value={primaryColor} />
<p>Secondary colour:</p><input class="input my-auto mx-auto" type="color" bind:value={secondaryColor} />
<p>Tertiary colour:</p><input class="input my-auto mx-auto" type="color" bind:value={tertiaryColor} />
<p>Description:</p><p>{description}</p>
<p>Header:</p><p>{header_description}</p>
<p>Footer:</p><p>{footer_description}</p>
<p>Actions:</p>
    <div class="flex space-x-4">
    {#each action_arr as a}<div>{a.name}</div>{/each}
</div>
<p>Assets:</p>
<div class="flex space-x-4">
    {#each assets as i}<div>{i.img}</div>{/each}
</div>
<button class="btn variant-filled" on:click={proceed}>confirm</button>
</div>
{/if}
</div>