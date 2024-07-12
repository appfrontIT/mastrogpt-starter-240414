<script lang="ts">
    import { user, chat_room, selector, getCurrentTimestamp } from "../store";
    import { onMount } from "svelte";
    import { AppBar, getModalStore, FileButton, popup } from '@skeletonlabs/skeleton';
	import { DataHandler } from "@vincjo/datatables";
    import type { Readable, Writable } from 'svelte/store';

    const modalStore = getModalStore();
    const reader = new FileReader();
    let name: string = '';
    let description: string = '';
    let header_check: Boolean = false;
    let header_description: string = '';
    let footer_check: Boolean = false;
    let footer_description: string = '';
    let files: FileList = null;
    let url = null;
    let text_data = null;
    let collections_promise;
    let handler: DataHandler<any>;
    let rows: Readable<any[]>;
    let value: string;


    onMount(async () => {
    })
    
    let col_name: string = null;
    async function onChangeHandler(e: Event) {
        // var data = new FormData()
        // data.append('file', files[0])
        // const r = await fetch('https://tmpfiles.org/api/v1/upload', {
        //     method: 'POST',
        //     body: data
        // })
        // const obj = await r.json()
        // file = obj.data['url']
        reader.readAsText(files[0])
        col_name = files[0].name + '-' + new Date().toLocaleString();
        col_name = col_name.replaceAll(' ', '-').replaceAll(':', '-').replaceAll('/', '_');
        modalStore.trigger({
            type: 'component',
            component: 'modalWaiting',
            meta: { msg: "uploading file..." }
        });
        while(reader.readyState == 1) {
            await new Promise(r => setTimeout(r, 1000));
        }
        const result = reader.result.toString();
        const split_res = result.split('\n');
        const header = split_res[0];
        for (let n = 1; n < files[0].size; n += 10000) {
            const slice = split_res.slice(n, n + 10000);
            if (slice.length == 0) { break; }
            const data = header + '\n' + slice.join('\n');
            const r = await fetch('/api/my/db/mongo/mastrogpt/' + col_name + '/add_csv', {
                method: "POST",
                headers: {"Authorization": "Bearer " + $user['JWT'], "Content-Type": "application/json"},
                body: JSON.stringify({'data': data})
            })
            if (slice.length < 10000) { break; }
            if (!r.ok) {
                alert('something went wrong during update');
                modalStore.close();
                return;
            }
        }
        modalStore.close();
        alert('collection creata con successo!');
    }

    async function get_collections() {
        const r = await fetch('/api/my/db/mongo/mastrogpt/get_collections', {
            method: "GET",
            headers: {"Authorization": "Bearer " + $user['JWT']}
        })
        if (r.ok) {
            const obj = await r.json();
            handler = new DataHandler(obj);
            rows = handler.getRows();
            return obj;
        }
        return null;
    }

    async function proceed() {
        const chart_type = document.getElementsByName('radio-direct');
        let type = null;
        for (let i = 0; i < chart_type.length; i++) {
            const el = chart_type[i] as HTMLInputElement;
            if (el.checked) {
                type = el.value;
            }
        }
        if (!type) { alert("Devi selezionare un tipo di grafico!"); return ;}
        if (name === '') { alert('Nome mancante'); return ;}
        if (description === '') { alert('Descrizione mancante'); return ;}
        if (!col_name && !url && !text_data) {
            alert("Devi specificare uno o piú dati da visualizzare nel grafico"); return ;
        }
        // modalStore.trigger({
        //     type: 'component',
        //     component: 'modalWaiting',
        //     meta: { msg: "Sto generando il grafico, per favore attendi" }
        // });
        let query = "create a chart using the following guidelines:"
        query += `\nChart type: ${type}\n Page name: ${name}\nDescription: ${description}`;
        if (header_check) {
            query += `\nPage header: ${header_description}`
        }
        if (footer_check) {
            query += `\nPage footer: ${footer_description}`
        }
        if (col_name) { query += `'collection': ${col_name}`}
        if (text_data) { query += `'text': ${text_data}`}
        if (url) { query += `'url': ${url}`}
        $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': query}]
        const data = JSON.stringify({'input': $chat_room[$selector].history});
        const response = await fetch($chat_room[$selector].url, {
			method: 'POST',
			body: data,
			headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + $user!['JWT']}
		})
        // modalStore.close();
    }

    async function check_dataset(name) {
        const r = await fetch('/api/my/db/mongo/mastrogpt/' + name + '/find_many?n_results=200&fields=' + encodeURIComponent(JSON.stringify({'_id': 0})), {
            method: "GET",
            headers: {"Authorization": "Bearer " + $user['JWT']}
        })
        if (r.ok) {
            const obj = await r.json();
            modalStore.trigger({
                type: 'component',
                component: 'modalData',
                meta: { msg: JSON.stringify(obj, null, "\t"), title: name }
            });
            return obj;
        }
        return null;
    }

</script>
<div class="space-y-2">
<p class="h5">Chart type:</p>
<AppBar background="0x44000000">
    <svelte:fragment slot="lead">
            <label class="flex space-x-2">
                <input class="radio" type="radio" name="radio-direct" value="Area"/>
                <p>Area</p>
                <input class="radio" type="radio" name="radio-direct" value="Bar"/>
                <p>Bar</p>
                <input class="radio" type="radio" name="radio-direct" value="Bubble"/>
                <p>Bubble</p>
                <input class="radio" type="radio" name="radio-direct" value="Doughnut"/>
                <p>Doughnut</p>
                <input class="radio" type="radio" name="radio-direct" value="Pie"/>
                <p>Pie</p>
                <input class="radio" type="radio" name="radio-direct" value="Line"/>
                <p>Line</p>
                <input class="radio" type="radio" name="radio-direct" value="Polar Area"/>
                <p>Polar Area</p>
                <input class="radio" type="radio" name="radio-direct" value="Radar"/>
                <p>Radar</p>
                <input class="radio" type="radio" name="radio-direct" value="Scatter"/>
                <p>Scatter</p>
            </label>
    </svelte:fragment>
    <svelte:fragment slot="trail">
        <button type="button" class="btn btn-md variant-filled" on:click={proceed}>procedi</button>
    </svelte:fragment>
</AppBar>
<p class="h5">Name:</p>
<div class="input-group input-group-divider grid-cols-[auto_1fr_auto]">
    <div class="input-group-shim">{$user.username}/</div>
    <input type="text" placeholder="https://walkiria.cloud/api/v1/web/gporchia/display/..." bind:value={name}/>
</div>
<p class="h5">Description:</p>
<textarea class="textarea" rows="2" placeholder="Enter a description to pass to the AI to generate your UI" bind:value={description}/>
<p class="h5">Layout:</p>
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
<p class="h5">Data:</p>
<div class="space-y-0">
    <p class="h5">collection:</p>
    <div class="flex space-x-4">
    <button class="btn [&>*]:pointer-events-none variant-ringed" use:popup={{event: 'click', target: 'collections_list', placement: 'top'}} on:click={() => {
        collections_promise = get_collections();
    }}>
        {#if col_name}
            {col_name}
        {:else}
            choose
        {/if}
    </button>
    <div class="card p-4 overflow-y-auto max-h-[50vh] shadow-xl " data-popup="collections_list">
        {#await collections_promise}
        ...loading collections
        {:then cols}
        {#if cols}
        <header class="flex">
            <input
                class="input sm:w-64 w-36"
                type="search"
                placeholder="Search..."
                bind:value
                on:input={() => handler.search(value)} />
            </header>
            <table class="table table-hover table-comfortable w-full">
                <tbody>
            {#each $rows as col, i}
            <tr>
            <div class="grid grid-cols-12 p-1">
                <div class="grid col-span-10">
                    {col}
                </div>
                <button class="btn btn-sm variant-filled self-end" on:click={() => {col_name = col}}>choose</button>
                <button class="btn btn-sm variant-filled self-end" on:click={() => check_dataset(col)}>look</button>
            </div>
            </tr>
            {/each}
        </tbody>
        </table>
        {/if}
        {/await}
    </div>
    <FileButton name="files" button="btn variant-ringed" accept=".csv" bind:files={files} on:change={onChangeHandler}>CSV</FileButton >
    <FileButton name="files" button="btn variant-ringed" accept=".pdf" bind:files={files} on:change={onChangeHandler}>PDF</FileButton >
    </div>
<p class="h5">url:</p>
<input class="input" title="Input (url)" type="url" placeholder="example.com" bind:value={url}/>
<p class="h5">text:</p>
<textarea class="textarea" rows="3" placeholder="Enter a description to pass to the AI to generate your UI" bind:value={text_data}/>
</div>
</div>