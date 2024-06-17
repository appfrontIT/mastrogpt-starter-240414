<script lang="ts">
    import { user, chat_room, selector, getCurrentTimestamp } from "../store";
    import { onMount } from "svelte";
    import { AppBar, getModalStore, FileButton } from '@skeletonlabs/skeleton';

    const modalStore = getModalStore();
    const reader = new FileReader();
    let name: string = '';
    let description: string = '';
    let header_check: Boolean = false;
    let header_description: string = '';
    let footer_check: Boolean = false;
    let footer_description: string = '';
    let files: FileList = null;
    let file = null;
    let url = null;
    let text_data = null;

    onMount(async () => {
    })
    
    async function onChangeHandler(e: Event) {
        // const response = await fetch('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/presignedUrl?name=' + `${$user.username}/${files[0].name}`, {
        //     method: "GET",
        //     headers: {"Authorization": "Bearer " + $user!['JWT']},
        // })
        // if (response.status == 200) {
        //     const url = await response.text();
        //     const upload_r = await fetch(url, {
        //         method: 'PUT',
        //         body: files[0]
        //     });
        // if (upload_r.ok) {
        //         alert(`file uploaded at https://gporchia.nuvolaris.dev/${$user.username}/${files[0].name}`)
        //     }
        // }
        // reader.readAsText(files[0])
        // while(reader.readyState == 1) {
        //     await new Promise(r => setTimeout(r, 1000));
        // }
        // console.log(reader.result)
        var data = new FormData()
        data.append('file', files[0])
        const r = await fetch('https://tmpfiles.org/api/v1/upload', {
            method: 'POST',
            body: data
        })
        const obj = await r.json()
        file = obj.data['url']
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
        if (!files && !url && !text_data) {
            alert("Devi specificare uno o piú dati da visualizzare nel grafico"); return ;
        }
        let query = "create a chart using the following guidelines:"
        query += `\nChart type: ${type}\n Page name: ${name}\nDescription: ${description}`;
        if (header_check) {
            query += `\nPage header: ${header_description}`
        }
        if (footer_check) {
            query += `\nPage footer: ${footer_description}`
        }
        $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': query}]
        const data = JSON.stringify({'input': $chat_room[$selector].history, 'name': name, 'id': $user!['_id'], 'data': {'file': file, 'text': text_data, 'url': url}});
        const response = await fetch($chat_room[$selector].url, {
			method: 'POST',
			body: data,
			headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + $user!['JWT']}
		})
        $selector = 1;
    }

</script>
<div class="space-y-4" style="height: 80vh;">
<p class="h4">Chart type:</p>
<AppBar background="0x44000000">
    <svelte:fragment slot="lead">
        <div class="flex">
            <label class="flex space-x-4">
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
        </div>
    </svelte:fragment>
    <svelte:fragment slot="trail">
        <button type="button" class="btn btn-md variant-filled" on:click={proceed}>procedi</button>
    </svelte:fragment>
</AppBar>
<p class="h4">Name:</p>
<div class="input-group input-group-divider grid-cols-[auto_1fr_auto]">
  <div class="input-group-shim">{$user.username}/</div>
  <input type="text" placeholder="https://nuvolaris.dev/api/v1/web/gporchia/display/..." bind:value={name}/>
</div>
<p class="h4">Description:</p>
<textarea class="textarea" rows="2" placeholder="Enter a description to pass to the AI to generate your UI" bind:value={description}/>
<p class="h4">Layout:</p>
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
<p class="h4">Data:</p>
<div class="space-y-0">
<p class="h5">file:</p>
<input class="input" type="file" accept=".csv" bind:files on:change={onChangeHandler}/>
<p class="h5">url:</p>
<input class="input" title="Input (url)" type="url" placeholder="example.com" bind:value={url}/>
<p class="h5">text:</p>
<textarea class="textarea" rows="3" placeholder="Enter a description to pass to the AI to generate your UI" bind:value={text_data}/>
</div>
</div>