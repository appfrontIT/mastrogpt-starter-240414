<script lang="ts">
    import fullscreen_icon from '$lib/assets/fullscreen.svg'
    import CodeMirror from "svelte-codemirror-editor";
    import { javascript } from "@codemirror/lang-javascript";
    import { python } from "@codemirror/lang-python";
    import { php } from "@codemirror/lang-php";
    import { html } from "@codemirror/lang-html";
    import { go } from "@codemirror/lang-go";
    import { oneDark } from "@codemirror/theme-one-dark";
    import {EditorView, keymap} from "@codemirror/view"
    // import {defaultKeymap} from "@codemirror/commands"
    import { chat_room, selector, user, editor } from '../store'
    import { DataHandler } from '@vincjo/datatables';
	// import { onMount } from 'svelte';
    import { getModalStore, getToastStore, popup } from '@skeletonlabs/skeleton';
    import type { PopupSettings, ToastSettings } from '@skeletonlabs/skeleton';
    import { type ModalSettings } from '@skeletonlabs/skeleton';
    import type { Readable, Writable } from 'svelte/store';
    import { TreeView, TreeViewItem } from '@skeletonlabs/skeleton';
			
    const modalStore = getModalStore();

    const modalFs: ModalSettings = {
        type: 'component',
        component: 'modalFs',
    };

    const popupFullscreen: PopupSettings = { event: 'hover', target: 'popupFullscreen', placement: 'left' };
    const popupTest: PopupSettings = { event: 'hover', target: 'popupTest', placement: 'left' };
    const popupVerify: PopupSettings = { event: 'hover', target: 'popupVerify', placement: 'left' };
    const popupWatch: PopupSettings = { event: 'hover', target: 'popupWatch', placement: 'left' };
    const popupDeploy: PopupSettings = { event: 'hover', target: 'popupDeploy', placement: 'left' };
    
    let view: EditorView;
    let handler: DataHandler<any>;
    let page_handler: DataHandler<any>;
    let value: string;
    let page_value: string;
    let watch_toggle = false;

    const toastStore = getToastStore();

    const languages_func = new Map<string, any>([
        ['go', go()],
        ['html', html()],
        ['javascript', javascript()],
        ['php', php()],
        ['python', python()],
    ]);
    const languages = ['go', 'html', 'javascript', 'php', 'python'];

    let props: CodeMirror["$$prop_def"] = {
        basic: true,
        useTab: true,
        editable: true,
        lineWrapping: false,
        readonly: false,
        tabSize: 2,
        placeholder: null,
        lang: null,
        theme: null,
        nodebounce: false
    };

    // onMount(async () => {})

    async function test() {
        if ($chat_room[$selector].editor.name === "" || $chat_room[$selector].editor.package === "") {
            alert('I need the package and the action name to perform the tests');
            return ;
        }
        const action = await fetch(`api/my/base/action/find?package=${$chat_room[$selector].editor.package}&name=${$chat_room[$selector].editor.name}`, {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
            method: 'GET'
        })
        if (action.status == 404) {
            var confirm_deploy = confirm('The action must be deployed to perform the tests. Do you wanna deploy it?')
            if (confirm_deploy) {
                await deploy();
            } else {
                return ;
            }
        }
        let query = `esegui i test sulla seguente azione: nome: ${$chat_room[$selector].editor.name}, package: ${$chat_room[$selector].editor.package}. Non chiedere conferma e comincia subito con i test`;
        const r = await fetch('api/my/base/invoke/walkiria', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
            method: 'POST',
            body: JSON.stringify({"input": query})
        })
    }

    async function verify() {
        let query = `analizza il codice seguente e mostrami se e dove ci sono degli errori, in piú suggerisci dei miglioramenti se ne hai.\nCodice:\n${$chat_room[$selector].editor.function}`;
        $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': query}]
        const r = await fetch('api/my/base/invoke/walkiria', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
            method: 'POST',
            body: JSON.stringify({"input": $chat_room[$selector].history})
        })
    }

    async function watch() {
        if (watch_toggle) {
            watch_toggle = false;
            $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': "grazie del supporto. Esci dalla modalitá 'watch'"}]
            const r = await fetch('api/my/base/invoke/walkiria', {
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
                method: 'POST',
                body: JSON.stringify({"input": $chat_room[$selector].history})
            })
            return;
        }
        watch_toggle = true
        let query = "da ora in poi, considerati in modalitá 'watch', fintanto che non ti comunicheró di smettre. Ti invieró periodicamente dei frammenti di codice. Osserva il codice, e se necessario comunicami gli errori e suggeriscimi le modifiche. Rsipondi con messaggi sintetici e concisi. Se pensi che vada tutto bene, rispondi in pochissime parole che il codice sembra corretto. Comincia chiedendomi che tipo di azione voglio creare. Inoltre, leggi attentamente i commenti per capire cosa il codice dovrebbe fare.";
        $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': query}]
        const r = await fetch('api/my/base/invoke/walkiria', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
            method: 'POST',
            body: JSON.stringify({"input": $chat_room[$selector].history})
        })
        while (watch_toggle) {
            await new Promise(r => setTimeout(r, 20000));
            if ($chat_room[$selector].editor.function === "") { continue; }
            $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': $chat_room[$selector].editor.function}]
            const r = await fetch('api/my/base/invoke/walkiria', {
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
                method: 'POST',
                body: JSON.stringify({"input": $chat_room[$selector].history})
            })
        }
    }

    async function deploy() {
        if ($chat_room[$selector].editor.language === "html") {
            if ($chat_room[$selector].editor.name === "") { alert('Provide a name for the page'); return; }
            modalStore.trigger({
                type: 'component',
                component: 'modalWaiting',
                meta: { msg: "Sto caricando la tua pagina, per favore attendi" }
            });
            let file = new File([$chat_room[$selector].editor.function], $chat_room[$selector].editor.name + '.html', {type: "text/html", endings: "native"})
            const response = await fetch('api/my/db/minio/static/presignedUrl?name=' + `${$user.username}/${file.name}`, {
                method: "GET",
                headers: {"Authorization": "Bearer " + $user!['JWT']},
            })
            if (response.status == 200) {
                const url = await response.text();
                const upload_r = await fetch(url, {
                    method: 'PUT',
                    body: file
                });
                if (upload_r.ok) {
                    const t: ToastSettings = {
                        message: 'La tua pagina é stata caricata con successo! Per accederla visitare: ' + `https://walkiria.cloud/${$user.username}/${file.name}`,
                        autohide: false,
                        action: { label: 'Visit', response: () => window.open(`https://walkiria.cloud/${$user.username}/${file.name}`)}
                    }
                    toastStore.trigger(t);
                }
            }
            modalStore.close();
            return ;
        }
        if ($chat_room[$selector].editor.name === "" || $chat_room[$selector].editor.description === "" || $chat_room[$selector].editor.language === "Language" || $chat_room[$selector].editor.package === "") {
            alert('You must fill all fields before deploying an action')
            return ;
        }
        modalStore.trigger({
                type: 'component',
                component: 'modalWaiting',
                meta: { msg: "Ricerca del package in corso..." }
            });
        const pack = await fetch('api/my/base/package/find?name=' + $chat_room[$selector].editor.package, {
            method: 'GET',
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
        })
        modalStore.close();
        if (pack.status != 200) {
            var confirm_package = confirm(`The package ${$chat_room[$selector].editor.package} does not exist, do you wanna create it?`)
            if (confirm_package) {
                modalStore.trigger({
                    type: 'component',
                    component: 'modalWaiting',
                    meta: { msg: "Creazione del package in corso..." }
                });
                const create_package = await fetch('api/my/base/package/add', {
                    method: 'POST',
                    headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
                    body: JSON.stringify({"name": $chat_room[$selector].editor.package})
                })
                if (create_package.status != 200) {
                    alert('there was an error while creating your package.')
                    return;
                }
                modalStore.close();
            } else {
                return ;
            }
        }
        const func = $chat_room[$selector].editor.function
        modalStore.trigger({
                type: 'component',
                component: 'modalWaiting',
                meta: { msg: "Deploy dell'azione in corso..." }
            });
        const upload = await fetch('api/my/base/action/add', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user['JWT']},
            method: "PUT",
            body: JSON.stringify({
                "name": $chat_room[$selector].editor.name,
                "function": func,
                "description": $chat_room[$selector].editor.description,
                "namespace": "gporchia/" + $chat_room[$selector].editor.package,
                "package": $chat_room[$selector].editor.package,
                "language": $chat_room[$selector].editor.language
            })
        })
        modalStore.close();
        if (upload.ok) {
            toastStore.trigger({
                message: 'Action succesfully deployed',
                autohide: false,
            });
        } else {
            toastStore.trigger({
                message: 'An error occured while deploying your action: ' + await upload.text(),
                autohide: false,
            });
        }
    }

    function clear() {
        $chat_room[$selector].editor = {
            'package': '',
            'name': '',
            'function': '',
            'description': '',
            'language': ''
        }
        $chat_room[$selector].showEditor = false;
    }

    async function fullscreen() {
        modalStore.trigger(modalFs);
    }

    const action_promise = action_list();
    let rows: Readable<any[]>;
    async function action_list() {
        const r = await fetch('/api/my/base/action/find_all', {
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

    const pages_promise = pages_list();
    let page_rows: Readable<any[]>;
    async function pages_list() {
        const r = await fetch(`/api/my/db/minio/static/find_all`, {
            method: "GET",
            headers: {"Authorization": "Bearer " + $user['JWT']}
        })
        if (r.ok) {
            const obj = await r.json();
            page_handler = new DataHandler(obj);
            page_rows = page_handler.getRows();
            return obj;
        }
        return null;
    }

    async function load_action(name: string, pack: string) {
        modalStore.trigger({
            type: 'component',
            component: 'modalWaiting',
            meta: { msg: "Recupero informazioni dell'action..." }
        });
        const r = await fetch(`/api/my/base/action/find?name=${name}&package=${pack}`, {
            method: "GET",
            headers: {"Authorization": "Bearer " + $user['JWT']}
        })
        modalStore.close();
        if (r.ok) {
            const obj = await r.json();
            $chat_room[$selector].editor.name = obj.name;
            $chat_room[$selector].editor.package = obj.namespace.split('/')[1];
            $chat_room[$selector].editor.function = obj.exec.code;
            for (let i = 0; i < obj.annotations.length; i++) {
                if (obj.annotations[i].key === "description") {
                    $chat_room[$selector].editor.description = obj.annotations[i].value;
                    break;
                }
            }
            $chat_room[$selector].editor.language = obj.exec.kind.split(':')[0];
            if ($chat_room[$selector].editor.language === 'nodejs') $chat_room[$selector].editor.language = 'javascript';
            return;
        }
        return null;
    }

    async function load_page(name: string) {
        modalStore.trigger({
            type: 'component',
            component: 'modalWaiting',
            meta: { msg: "Recupero informazioni della pagina..." }
        });
        const response = await fetch(`api/my/db/minio/static/find?name=${$user['username']}/name`, {
            method: "GET",
            headers: {"Authorization": "Bearer " + $user['JWT']},
        })
        modalStore.close();
        if (response.ok) {
            const obj = await response.json();
            $chat_room[$selector].editor.name = name.replace('.html', '');
            $chat_room[$selector].editor.package = $user['username'];
            $chat_room[$selector].editor.function = obj.data;
            $chat_room[$selector].editor.language = 'html';
            return;
        }
        return null;
    }

</script>
<div class="grid grid-rows-[1fr_auto]">
<div class="grid grid-cols-12 gap-4 space-y-1" style="height: 5vh;">
        <input class="input col-span-4" title="Action name" type="text" placeholder="action name" bind:value={$chat_room[$selector].editor.name}>
        {#if $chat_room[$selector].editor.language != 'html'}
        <input class="input col-span-4" title="Description" type="text" placeholder="description" bind:value={$chat_room[$selector].editor.description}/>
        <select class="select col-span-2" bind:value={$chat_room[$selector].editor.package}>
            <option disabled selected value>Package</option>
            {#each $user.package as pack}
                <option value={pack}>{pack}</option>
            {/each}
        </select>
        {/if}
        <select class="select col-span-2" bind:value={$chat_room[$selector].editor.language}>
            <option disabled selected value>Language</option>
            {#each languages as lang}
            <option value={lang}>{lang}</option>
            {/each}
        </select>
</div>
    <div class="grid h-full grid-rows-[1fr_auto] grid-cols-12" style="height: 80vh;">
    <CodeMirror
        bind:value={$chat_room[$selector].editor.function}
        lang={languages_func.get($chat_room[$selector].editor.language)}
        theme={oneDark}
        class="col-span-11 max-h-[80vh] overflow-y-auto"
        styles={{
            "&": {
                maxWidth: "100%",
                height: "80vh",
            },
        }}
        />
        <div class="grid grid-rows-10 space-y-2" style="height: 80vh;">
            <button class="btn [&>*]:pointer-events-none" on:click={fullscreen} use:popup={popupFullscreen}><img src={fullscreen_icon} alt="expand to fullscreen"></button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupFullscreen">
                <p>Questo bottone imposta l'editor a schermo interno</p>
            </div>
            {#if $selector == 2}
            <button class="btn [&>*]:pointer-events-none" on:click={test} use:popup={popupTest}>Test</button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupTest">
                <p>Utilizza questo bottone per testare l'azione all'interno dell'editor!<br>
                    Importante: per testare l'azione bisogna che sia prima fatto il deploy.<br>
                    L'azione viene testata utilizzando l'endpoint corrispettivo.
                </p>
            </div>
            <button class="btn [&>*]:pointer-events-none {watch_toggle === true ? 'variant-filled' : ''}" on:click={watch} use:popup={popupWatch}>Watch</button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupWatch">
                <p>Questo bottone attiverá la modalitá Watch.<br>
                    In questa modalitá l'AI continuerá periodicamente a darti feedback<br>
                    relativi al codice che hai scritto.<br>
                    Un modo intelligente di utilizzare questa modalitá é inserendo commenti<br>
                    all'interno del codice, che possano funzionare come 'suggerimenti' per il bot.
                </p>
            </div>
            <button class="btn [&>*]:pointer-events-none" on:click={verify} use:popup={popupVerify}>Verify</button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupVerify">
                <p>Questo bottone invia il codice scritto al bot per avere feedback e suggerimenti</p>
            </div>
            <button class="btn [&>*]:pointer-events-none" use:popup={{event: 'click', target: 'actions_list', placement: 'left'}}>Actions</button>
            <div class="card p-4 overflow-y-auto max-h-[70vh] shadow-xl" data-popup="actions_list">
                {#await action_promise}
                    <p>...loading actions</p>
                {:then act}
                {#if act}
                <header class="flex">
                    <input
                        class="input sm:w-64 w-36"
                        type="search"
                        placeholder="Search..."
                        bind:value
                        on:input={() => handler.search(value)} />
                    </header>
                    <table class="table table-hover table-compact table-auto w-full">
                    <tbody>
                    {#each $rows as a}
                    <tr>
                    <TreeView>
                        <TreeViewItem>
                        <div class="grid grid-cols-12 gap-4">
                            <div class="grid col-span-11">{a.name}</div>
                            <button class="btn btn-sm variant-filled self-end" on:click={() => {load_action(a.name, a.package)}}>edit</button>
                        </div>
                            <svelte:fragment slot="children">
                                <TreeViewItem>
                                    <svelte:fragment slot="lead">Package:</svelte:fragment>
                                    <p>{a.package}</p>
                                </TreeViewItem>
                                <TreeViewItem>
                                    <svelte:fragment slot="lead">Url:</svelte:fragment>
                                    <p>{a.url}</p>
                                </TreeViewItem>
                                <TreeViewItem>
                                    annotations:
                                    <svelte:fragment slot="children">
                                        {#each a.annotations as v}
                                            <TreeViewItem>
                                                <svelte:fragment slot="lead">{v.key}</svelte:fragment>
                                                {v.value}
                                                </TreeViewItem>
                                            {/each}
                                    </svelte:fragment>
                                </TreeViewItem>
                            </svelte:fragment>
                        </TreeViewItem>
                    </TreeView>
                    </tr>
                    {/each}
                </tbody>
                </table>
                {/if}
                {/await}
            </div>
            {/if}
            <button class="btn [&>*]:pointer-events-none" use:popup={{event: 'click', target: 'page_list', placement: 'left'}}>Pages</button>
            <div class="card p-4 overflow-y-auto max-h-[70vh] shadow-xl" data-popup="page_list">
                {#await pages_promise}
                    <p>...loading pages</p>
                {:then pages}
                {#if pages}
                <header class="flex">
                    <input
                        class="input sm:w-64 w-36"
                        type="search"
                        placeholder="Search..."
                        bind:value
                        on:input={() => page_handler.search(value)} />
                </header>
                <table class="table table-hover table-compact table-auto w-full">
                    <tbody>
                    {#each $page_rows as page}
                    {#if page.endsWith(".html")}
                    <tr>
                    <div class="grid grid-cols-12 gap-4 p-4">
                        <div class="grid col-span-11">{page}</div>
                        <button class="btn btn-sm variant-filled self-end" on:click={() => {load_page(page)}}>edit</button>
                    </div>
                    </tr>
                    {/if}
                    {/each}
                    </tbody>
                </table>
                {/if}
                {/await}
            </div>
            <button class="btn btn row-start-9" on:click={clear}>
                Clear
            </button>
            <button class="btn row-start-10 [&>*]:pointer-events-none" on:click={deploy} use:popup={popupDeploy}>Deploy</button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupDeploy">
                <p>Questo bottone fa il Deploy l'action all'interno dell'ambiente serverless.<br>
                    L'action ha bisogno che ogni campo sia compilato per essere deployata.<br>
                    La descrizione é importante per mantenere un ambiente sostenibile e per aiutare l'AI nelle sue operazioni    
                </p>
            </div>
        </div>
    </div>
</div>