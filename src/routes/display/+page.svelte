<script lang="ts">
    /** @type {import('./$types').PageData} */
	export let data;
    import { onMount } from "svelte";
    import { logged, selector, chat_room } from "../../store";
	import { getModalStore } from "@skeletonlabs/skeleton";

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
	});

    let pages = data.data;
    const user = data.user;

</script>
<div class="grid grid-cols-12 gap-4">
<nav class="list-nav col-start-2 col-end-11">
	<ul><br>
        {#each pages as page}
            {#if page.endsWith('.html')}
                <li class="flex space-x-2">
                    <a class="flex-auto" href={'https://gporchia.nuvolaris.dev/' + user.username + '/' + page} target="_blank">{page}</a>
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
