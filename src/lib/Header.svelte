<script lang="ts">
    import { set_dark_mode, user, logged } from "../store";
    import { AppBar, popup, Avatar,  } from "@skeletonlabs/skeleton";
    import type { PopupSettings } from '@skeletonlabs/skeleton';
    import { LightSwitch } from '@skeletonlabs/skeleton';
	import { onMount } from "svelte";

    let promise = get_user();
    const popupFeatured: PopupSettings = {
		event: 'click',
		target: 'popupFeatured',
		placement: 'bottom',
	};

    onMount(() => {
        set_dark_mode();
    })
    
    async function get_user() {
		const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })

		if (res.ok) { const obj = await res.json(); $user = obj; return obj; }
		else { throw new Error('failed to get user') };
	}

    async function logout() {
		const response = await fetch('api/my/base/auth/logout', {
			method: 'DELETE',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json'},
		});
		$user = null;
		$logged = false;
		document.cookie = 'appfront-sess-cookie=;expires=Thu, 01 Jan 1970 00:00:01 GMT'
        sessionStorage.clear()
        return window.parent.location.replace('/login')
	}
</script>

{#await promise then us}
<AppBar gridColumns="grid-cols-3" slotDefault="place-self-center" slotTrail="place-content-end">
	<svelte:fragment slot="lead">
		<h1 class="h1 font-bold"><span class="bg-gradient-to-br from-pink-500 to-violet-500 bg-clip-text text-transparent box-decoration-clone"><a href='/'>Walkiria</a></span></h1>
	</svelte:fragment>
    <LightSwitch />
	<svelte:fragment slot="trail">
        <div>
		<ol class="breadcrumb">
			<li class="crumb"><a class="anchor" href="/scraped">Scraped</a></li>
			<li class="crumb-separator" aria-hidden><span class="divider-vertical h-10" /></li>
			<li class="crumb"><a class="anchor" href="/swagger-ui">Swagger</a></li>
			<li class="crumb-separator" aria-hidden><span class="divider-vertical h-10" /></li>
			<li use:popup={popupFeatured}><Avatar
				initials={us.username[0]}
				border="border-4 border-surface-300-600-token hover:!border-primary-500"
				cursor="cursor-pointer"
			/></li>
			<div class="card p-4 w-72 shadow-xl z-10" data-popup="popupFeatured">
				<div><a class="btn" href='/my-swagger'>My Swagger</a></div>
				<div><a class="btn" href='/display'>My Pages</a></div>
				<div><a class="btn" href='/data'>My Files</a></div>
				<div><a class="btn" href="/settings">Settings</a></div>
				<div><button class="btn" on:click={logout}>Logout</button></div>
				<div class="arrow bg-surface-100-800-token" />
			</div>
		</ol>
    </div>
	</svelte:fragment>
</AppBar>
{:catch}
	{logout()}
{/await}