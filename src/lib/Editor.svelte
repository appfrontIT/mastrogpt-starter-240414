<script lang="ts">
    import fullscreen_icon from '$lib/fullscreen.svg'
    import CodeMirror from "svelte-codemirror-editor";
    import { javascript } from "@codemirror/lang-javascript";
    import { python } from "@codemirror/lang-python";
    import { php } from "@codemirror/lang-php";
    import { html } from "@codemirror/lang-html";
    import { go } from "@codemirror/lang-go";
    import { oneDark } from "@codemirror/theme-one-dark";
    import {EditorView, keymap} from "@codemirror/view"
    import {defaultKeymap} from "@codemirror/commands"
    import { chat_room, selector, user, editor } from '../store'
	import { onMount } from 'svelte';
    import { getToastStore, popup } from '@skeletonlabs/skeleton';
    import type { PopupSettings, ToastSettings } from '@skeletonlabs/skeleton';
    // import { Modal, type ModalComponent, type ModalSettings } from '@skeletonlabs/skeleton';
    // import ModalFs from './ModalFS.svelte';
    // import { getModalStore } from '@skeletonlabs/skeleton';
			
    // const modalStore = getModalStore();

    // const modalComponent: ModalComponent = { ref: ModalFs };

    // const modal: ModalSettings = {
    //     type: 'component',
    //     component: modalComponent,
    // };

    const popupFullscreen: PopupSettings = { event: 'hover', target: 'popupFullscreen', placement: 'left' };
    const popupTest: PopupSettings = { event: 'hover', target: 'popupTest', placement: 'left' };
    const popupVerify: PopupSettings = { event: 'hover', target: 'popupVerify', placement: 'left' };
    const popupWatch: PopupSettings = { event: 'hover', target: 'popupWatch', placement: 'left' };
    const popupDeploy: PopupSettings = { event: 'hover', target: 'popupDeploy', placement: 'left' };
    
    let view: EditorView;
    let value = "";
    let watch_toggle = false;
    let packages: string[] = [];

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
        if ($editor.name === "" || $editor.package === "") {
            alert('I need the package and the action name to perform the tests');
            return ;
        }
        const action = await fetch(`api/my/base/action/find?package=${$editor.package}&name=${$editor.name}`, {
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
        let query = `esegui i test sulla seguente azione: nome: ${$editor.name}, package: ${$editor.package}. Non chiedere conferma e comincia subito con i test`;
        const r = await fetch('api/my/base/invoke/walkiria', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
            method: 'POST',
            body: JSON.stringify({"input": query})
        })
    }

    async function verify() {
        let query = `analizza il codice seguente e mostrami se e dove ci sono degli errori, in piú suggerisci dei miglioramenti se ne hai.\nCodice:\n${$editor.function}`;
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
            await new Promise(r => setTimeout(r, 15000));
            if ($editor.function === "") { continue; }
            $chat_room[$selector].history = [...$chat_room[$selector].history, {'role': 'user', 'content': $editor.function}]
            const r = await fetch('api/my/base/invoke/walkiria', {
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
                method: 'POST',
                body: JSON.stringify({"input": $chat_room[$selector].history})
            })
        }
    }

    async function deploy() {
        if ($editor.language === "html") {
            if ($editor.name === "") { alert('Provide a name for the page'); return; }
            let file = new File([$editor.function], $editor.name + '.html', {type: "text/html", endings: "native"})
            const response = await fetch('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/presignedUrl?name=' + file.name, {
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
                        message: 'La tua pagina é stata caricata con successo! Per accederla visitare: ' + `https://gporchia.nuvolaris.dev/${$user.username}/${file.name}`,
                        autohide: false,
                        action: { label: 'Visit', response: () => window.open(`https://gporchia.nuvolaris.dev/${$user.username}/${file.name}`)}
                    }
                    toastStore.trigger(t);
                }
            }
            return ;
        }
        if ($editor.name === "" || $editor.description === "" || $editor.language === "Language" || $editor.package === "") {
            alert('You must fill all fields before deploying an action')
            return ;
        }
        const pack = await fetch('api/my/base/package/find?name=' + $editor.package, {
            method: 'GET',
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
        })
        if (pack.status != 200) {
            var confirm_package = confirm(`The package ${$editor.package} does not exist, do you wanna create it?`)
            if (confirm_package) {
                const create_package = await fetch('api/my/base/package/add', {
                    method: 'POST',
                    headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user!['JWT']},
                    body: JSON.stringify({"name": $editor.package})
                })
                if (create_package.status != 200) {
                    alert('there was an error while creating your package.')
                    return;
                }
            } else {
                return ;
            }
        }
        const func = $editor.function
        const upload = await fetch('api/my/base/action/add', {
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user['JWT']},
            method: "PUT",
            body: JSON.stringify({
                "name": $editor.name,
                "function": func,
                "description": $editor.description,
                "namespace": "gporchia/" + $editor.package,
                "package": $editor.package,
                "language": $editor.language
            })
        })
        if (upload.status == 200) {
            alert('action succesfully deployed!')
        }
    }

    async function fullscreen() {
        console.log('fullscreen')
    }

</script>
<div class="grid grid-cols-12 gap-4 space-y-1" style="height: 5vh;">
    <input class="input col-span-4" title="Action name" type="text" placeholder="action name" bind:value={$editor.name}>
    {#if $editor.language != 'html'}
    <input class="input col-span-4" title="Description" type="text" placeholder="description" bind:value={$editor.description}/>
    <select class="select col-span-2" bind:value={$editor.package}>
        <option disabled selected value>Package</option>
        {#each packages as pack}
            <option value={pack}>{pack}</option>
        {/each}
    </select>
    {/if}
    <select class="select col-span-2" bind:value={$editor.language}>
        <option disabled selected value>Language</option>
        {#each languages as lang}
        <option value={lang}>{lang}</option>
        {/each}
    </select>
</div>
<div class="grid h-full w-full grid-rows-[1fr_auto] grid-cols-11" style="height: 80vh;">
    <CodeMirror
        bind:value={$editor.function}
        lang={languages_func.get($editor.language)}
        theme={oneDark}
        class="col-span-10 max-h-[80vh] overflow-y-auto"
        styles={{
            "&": {
                maxWidth: "100%",
                height: "80vh",
            },
        }}
        />
        <div class="grid w-full grid-rows-10 space-y-2" style="height: 80vh;">
            <button class="btn [&>*]:pointer-events-none" on:click={fullscreen} use:popup={popupFullscreen}><img src={fullscreen_icon} alt="expand to fullscreen"></button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupFullscreen">
                <p>Questo bottone imposta l'$editor a schermo interno</p>
            </div>
            <button class="btn [&>*]:pointer-events-none" on:click={test} use:popup={popupTest}>Test</button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupTest">
                <p>Utilizza questo bottone per testare l'azione all'interno dell'$editor!<br>
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
            <button class="btn [&>*]:pointer-events-none">Actions</button>
            <button class="btn row-start-10 [&>*]:pointer-events-none" on:click={deploy} use:popup={popupDeploy}>Deploy</button>
            <div class="card p-4 variant-filled-secondary" data-popup="popupDeploy">
                <p>Questo bottone fa il Deploy l'action all'interno dell'ambiente serverless.<br>
                    L'action ha bisogno che ogni campo sia compilato per essere deployata.<br>
                    La descrizione é importante per mantenere un ambiente sostenibile e per aiutare l'AI nelle sue operazioni    
                </p>
            </div>
        </div>
</div>
