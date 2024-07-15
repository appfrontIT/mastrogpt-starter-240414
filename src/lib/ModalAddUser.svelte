<script lang="ts">
	import type { SvelteComponent } from 'svelte';
	import { getModalStore } from '@skeletonlabs/skeleton';
	import { user } from '../store';

	export let parent: SvelteComponent;
	const modalStore = getModalStore();

	const formData = {
		username: '',
		role: '',
	};

	// We've created a custom submit function to pass the response and close the modal.
	async function onFormSubmit() {
		const r = await fetch('api/my/base/user/add', {
			method: 'POST',
			headers: {"Content-Type": "application/json", 'Authorization': 'Bearer ' + $user['JWT']},
			body: JSON.stringify({'username': formData.username, 'password': formData.password, 'role': 'user'})
		})
		console.log(r.status)
		if (r.ok) {
			alert('User creato con successo');
			console.log(await r.json());
		} else {
			alert('Errore: ' + await r.text());
		}
		modalStore.close();
		return ;
	}

	// Base Classes
	const cBase = 'card p-4 w-modal shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const cForm = 'border border-surface-500 p-4 space-y-4 rounded-container-token';
</script>

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<header class={cHeader}>Add user</header>
		<form class="modal-form {cForm}">
			<label class="label">
				<span>Userame</span>
				<input class="input" type="text" bind:value={formData.username} placeholder="Enter username..." />
			</label>
			<label class="label">
				<span>Role</span>
				<select class="select" bind:value={formData.role}>
					<option value="user">user</option>
					<option value="admin">admin</option>
				</select>
			</label>
		</form>
		<!-- prettier-ignore -->
		<footer class="modal-footer {parent.regionFooter}">
			<button class="btn {parent.buttonNeutral}" on:click={parent.onClose}>{parent.buttonTextCancel}</button>
			<button class="btn {parent.buttonPositive}" on:click={onFormSubmit}>Submit Form</button>
		</footer>
	</div>
{/if}
