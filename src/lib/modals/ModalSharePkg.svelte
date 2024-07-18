<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';
    import { ProgressBar } from '@skeletonlabs/skeleton';
	import { user } from '../../store';

	export let parent: SvelteComponent;
	let users;
	let s;
	
	const modalStore = getModalStore();

	async function get_users() {
		const response = await fetch('api/my/base/user/find_all', {
			method: 'GET',
			headers: {"Authorization": "Bearer " + $user!['JWT']}
		})
		if (response.status != 200) {
			return null
		}
		users = await response.json();
		return users;
	}

	const cButton = 'fixed top-4 right-4 z-50 font-bold shadow-xl';
</script>

{#if $modalStore[0]}
	<div class="card p-4 w-modal shadow-xl space-y-4">
		{#await get_users()}
			...retrieving users
			{:then us} 
			<div class="input-group input-group-divider grid-cols-[1fr_auto]">
			<select class="select" bind:value={s}>
				{#each us as u}
					{#if u.role != 'admin' && u.role != 'root'}
						<option value={u._id}>{u.username}</option>
					{/if}
				{/each}
			</select>
			<button class="btn variant-filled" on:click={async() => {
				const response = await fetch('api/my/base/package/share', {
					method: "PUT",
					headers: {"Authorization": "Bearer " + $user.JWT, "Content-Type": "application/json" },
					body: JSON.stringify({'package': $modalStore[0].meta.package, 'id': s})
				})
			}}>share</button>
			</div>
			{/await}
	</div>
    <button class="btn-icon variant-filled {cButton}" on:click={parent.onClose}>×</button>
{/if}