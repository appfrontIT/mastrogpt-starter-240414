<script lang='ts'>
	import { user } from '../../store'
	import { onMount, onDestroy } from 'svelte';
	import { DataHandler } from '@vincjo/datatables';
	import type { Readable, Writable } from 'svelte/store';
	import { getModalStore, getToastStore, popup } from '@skeletonlabs/skeleton';
	import type { ToastSettings, ToastStore } from '@skeletonlabs/skeleton';
	import { type ModalComponent, type ModalSettings } from '@skeletonlabs/skeleton';
			
	const modalStore = getModalStore();
	const modal: ModalSettings = {
        type: 'component',
        component: 'modalAddUser',
    };
	
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
	
	const toastStore = getToastStore();
	const accepted: ToastSettings = {
		message: 'richiesta accettato',
	};
	const denyed: ToastSettings = {
		message: 'richiesta respinta',
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
		await get_pendings();
		handler_init();
	})
	
	async function get_pendings() {
		const response = await fetch('api/my/base/user/pendings', {
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

<div class=" overflow-x-auto space-y-2" style="height: 80vh;">
	<header class="flex justify-between gap-4">
		<input
			class="input sm:w-64 w-36"
			type="search"
			placeholder="Search..."
			bind:value
			on:input={() => handler.search(value)}
		/>
		<aside class="flex place-items-center">
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
                <th on:click={() => handler.sort('name')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'name'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					name
				</th>
                <th on:click={() => handler.sort('surname')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'surname'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					surname
				</th>
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
				<th on:click={() => handler.sort('email')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'email'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					email
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
				<tr>
					<td>{usr.name}</td>
					<td>{usr.surname}</td>
					<td>{usr.username}</td>
                    <td>{usr.email}</td>
					<td>
					<button class="btn btn-sm variant-ringed" on:click={async () => {
						const conf = confirm(`Accettare l'iscrizione dell'utente ${usr.username}?`);
                        if (conf) {
                            const response = await fetch('api/my/base/user/add', {
                                method: "POST",
                                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user.JWT},
                                body: JSON.stringify({"name": usr.name, "surname": usr.surname, "username": usr.username, "email": usr.email, "role": "user"})
                            })
                            if (response.ok) {
                                toastStore.trigger(accepted);
                                const index = users.indexOf(usr);
								users.splice(index, 1);
								handler_init();
                                const r = await fetch('/api/my/db/mongo/signup/delete?id=' + usr._id, {
                                    method: "DELETE",
                                    headers: {"Authorization": "Bearer " + $user.JWT},
                                })
                            }
                        }
					}}>accept</button>
					<button class="btn btn-sm variant-ringed" on:click={async () => {
						const conf = confirm(`Respingere l'iscrizione dell'utente ${usr.username}?`);
                        if (conf) {

                        }
					}}>deny</button>
					</td>
				</tr>
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