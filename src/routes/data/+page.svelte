<script lang="ts">
    import { onMount } from "svelte";
    import { logged } from "../../store";
    import { FileDropzone, getToastStore, getModalStore } from '@skeletonlabs/skeleton';
	import type { ToastSettings } from '@skeletonlabs/skeleton';
    /** @type {import('./$types').PageData} */
	export let data;

    let pages = data.data;
    let user = data.user;
    const reader = new FileReader();
    let files: FileList = null;
    const toastStore = getToastStore();
    const modalStore = getModalStore();

    onMount(async () => {
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
    })

    async function onChangeHandler() {
        modalStore.trigger({
            type: 'component',
            component: 'modalWaiting',
            meta: { msg: "Sto caricando la tua pagina, per favore attendi" }
        });
        reader.readAsArrayBuffer(files[0])
        while(reader.readyState == 1) {
            await new Promise(r => setTimeout(r, 1000));
        }
        const result = reader.result;
        const response = await fetch('https://nuvolaris.dev/api/v1/web/gporchia/db/minio/gporchia-web/presignedUrl?name=' + `${user.username}/${files[0].name}`, {
            method: "GET",
            headers: {"Authorization": "Bearer " + user!['JWT']},
        })
        if (response.status == 200) {
            const url = await response.text();
            const upload_r = await fetch(url, {
                method: 'PUT',
                body: result
            });
            if (upload_r.ok) {
                const t: ToastSettings = {
                    message: 'File caricato con successo!',
                    autohide: false,
                }
                pages.push(files[0].name);
                pages = pages;
                toastStore.trigger(t);
            }
        }
        modalStore.close();
    }

</script>
<div class="grid grid-cols-12 gap-4">
    <nav class="list-nav col-start-2 col-end-11"><br>
    <FileDropzone name="files" class="col-start-2 col-end-11" bind:files={files} on:change={onChangeHandler}/>
	<ul><br>
        {#each pages as page}
            {#if !page.endsWith('.html')}
                <li class="flex space-x-2">
                    <a class="flex-auto" href={'https://walkiria.cloud/' + user.username + '/' + page} target="_blank">{page}</a>
                    <button class="btn variant-filled" on:click={async () => {
                        const response = await fetch('/api/my/db/minio/gporchia-web/delete?name=' + user.username + '/' + page, {
                            method: 'DELETE',
                            headers: {'Authorization': 'Bearer ' + user.JWT}
                        })
                        const index = pages.indexOf(page);
                        if (index > -1) {
                            pages.splice(index, 1);
                            pages = pages;
                        }
                    }}>delete</button>
                </li>
            {/if}
        {/each}
            </ul>
</nav>
</div>