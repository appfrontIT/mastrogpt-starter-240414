<script lang='ts'>
	import { user } from '../../store'
	import { onMount, onDestroy } from 'svelte';
	import { DataHandler } from '@vincjo/datatables';
	import type { Readable, Writable } from 'svelte/store';
	import { getToastStore, popup } from '@skeletonlabs/skeleton';
	import type { ToastSettings, ToastStore } from '@skeletonlabs/skeleton';
	
	let users: any[] | null = [];
	let value: string;
	let handler: DataHandler<any>;
	let rows: Readable<any[]>;
	let sorted: Writable<{
		identifier?: string | undefined;
		direction?: "desc" | "asc" | undefined;
	}>;
	let rowCount: Readable<{
		total: number;
		start: number;
		end: number;
	}>;
	
	let pageNumber: Readable<number>;
	let pageCount: Readable<number>;
	let pages: Readable<number[]>;
	let rowsPerPage: Writable<number | null>;
	let options = [5, 10, 20, 50, 100];
	
	let add_username: string;
	let add_role: string;

	const toastStore = getToastStore();
	const delete_ok: ToastSettings = {
		message: 'Utente eliminata con successo!',
	};
	const delete_failure: ToastSettings = {
		message: 'Un problema é accorso durante il processo di eliminazione, per favore riprovare',
	};

	function handler_init() {
		handler = new DataHandler(users, {rowsPerPage: 5});
		rows = handler.getRows();
		rowCount = handler.getRowCount();
		sorted = handler.getSort();
		pageNumber = handler.getPageNumber();
		pageCount = handler.getPageCount();
		pages = handler.getPages({ ellipsis: true });
        pages = handler.getPages({ ellipsis: true });
		rowsPerPage = handler.getRowsPerPage();
	}

	onMount(async () => {
		await get_users();
		handler_init();
	})
	
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
	</script>

<div class="overflow-x-auto space-y-2" style="height: 80vh;">
	<header class="flex justify-between gap-4">
		<input
			class="input sm:w-58 w-36"
			type="search"
			placeholder="Search..."
			bind:value
			on:input={() => handler.search(value)}
		/>
		{#if $user.role == 'admin'}
			<div class="flex space-x-4">
				<input class="input w-64" placeholder="username" bind:value={add_username}/>
				<select class="select" bind:value={add_role}>
					<option value="user">user</option>
					<option value="admin">admin</option>
				</select>
				<button class="btn variant-filled" on:click={async() => {
					const response = await fetch('api/my/base/user/add', {
						method: 'POST',
						headers: {"Content-Type": "application/json", 'Authorization': 'Bearer ' + $user['JWT']},
						body: JSON.stringify({'username': add_username, 'role': add_role})
					})
					const obj = await response.json();
					if (response.ok) {
						toastStore.trigger({message: "User succesfully created.\nPassword: " + obj.password});
						await get_users();
						handler_init();
					} else {
						toastStore.trigger({message: obj.error})
					}
				}}>add</button>
			</div>
		{/if}
		<aside class="flex place-items-center sm:w-58 w-36">
			Show
			{#if rowsPerPage}
			<select class="select ml-2" bind:value={$rowsPerPage}>
				{#each options as option}
					<option value={option}>
						{option}
					</option>
				{/each}
			</select>
			{/if}
		</aside>
	</header>
	<table class="table table-hover table-compact table-auto w-full">
		<thead>
			<tr>
				{#if handler && $sorted}
				<th on:click={() => handler.sort('username')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'username'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					username
				</th>
				<th on:click={() => handler.sort('package')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'package'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					package
				</th>
				<th on:click={() => handler.sort('role')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'role'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					role
				</th>
				<th class="table-cell-fit">
					opt
				</th>
				{/if}
			</tr>
		</thead>
		<tbody>
			{#if rows}
			{#each $rows as usr}
			{#if usr.role != 'root' && usr.username != $user.username}
				<tr>
					<td>{usr.username}</td>
					<td>{usr.package}</td>
					<td>{usr.role}</td>
					{#if $user.role == 'admin'}
					<td>
					<button class="btn btn-sm variant-ringed" on:click={async () => {
						const conf = confirm('Sei sicuro di voler eliminare questo utente?');
							if (conf) {
								const response = await fetch(`/api/my/base/user/delete?id=${usr._id}`, {
									method: 'DELETE',
									headers: {"Authorization": "Bearer " + $user['JWT']}
								})
								if (response.ok) {
									toastStore.trigger(delete_ok);
									await get_users();
									handler_init();
								} else {
									toastStore.trigger(delete_failure);
								}
							}
					}}>Delete</button>
					</td>
					{/if}
				</tr>
			{/if}
			{/each}
			{/if}
		</tbody>
	</table>
	<footer class="flex justify-between">
        <!-- <RowCount {handler} /> -->
		<aside class="text-sm leading-8 mr-6">
			{#if $rowCount && $rowCount.total > 0}
				<b>{$rowCount.start}</b>
				- <b>{$rowCount.end}</b>
				/ <b>{$rowCount.total}</b>
			{:else}
				No entries found
			{/if}
		</aside>
        <!-- <Pagination {handler} /> -->
		<!-- Desktop buttons -->
		<section class="btn-group variant-ghost-surface [&>*+*]:border-surface-500 h-10 hidden lg:block">
			<button
				type="button"
				class="hover:variant-soft-primary"
				class:disabled={$pageNumber === 1}
				on:click={() => handler.setPage('previous')}
			>
				←
			</button>
			{#if $pages}
			{#each $pages as page}
				<button
					type="button"
					class="hover:variant-soft-primary"
					class:active={$pageNumber === page}
					class:ellipse={page === null}
					on:click={() => handler.setPage(page)}
				>
					{page ?? '...'}
				</button>
			{/each}
			{/if}
			<button
				type="button"
				class="hover:variant-soft-primary"
				class:disabled={$pageNumber === $pageCount}
				on:click={() => handler.setPage('next')}
			>
				→
			</button>
		</section>

		<!-- Mobile buttons -->
		<section class="lg:hidden">
			<button
				type="button"
				class="btn variant-ghost-surface mr-2 mb-2 hover:variant-soft-primary"
				class:disabled={$pageNumber === 1}
				on:click={() => handler.setPage('previous')}
			>
				←
			</button>
			<button
				type="button"
				class="btn variant-ghost-surface mb-2 hover:variant-soft-primary"
				class:disabled={$pageNumber === $pageCount}
				on:click={() => handler.setPage('next')}
			>
				→
			</button>
		</section>
    </footer>
</div>