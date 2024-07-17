<script lang='ts'>
	import { user } from '../../store'
	import { onMount, onDestroy } from 'svelte';
	import { DataHandler } from '@vincjo/datatables';
	import type { Readable, Writable } from 'svelte/store';
	import { getModalStore, getToastStore, popup } from '@skeletonlabs/skeleton';
	import type { ToastSettings, ToastStore } from '@skeletonlabs/skeleton';
	
	let packages: any[] | null = [];
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

	let add_package: string;
	
	const toastStore = getToastStore();
	const delete_ok: ToastSettings = {
		message: 'Package eliminata con successo!',
	};
	const delete_failure: ToastSettings = {
		message: 'Un problema é accorso durante il processo di eliminazione, per favore riprovare',
	};

	function handler_init() {
		handler = new DataHandler(packages, {rowsPerPage: 5});
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
		await get_packages();
		handler_init();
	})
	
	async function get_packages() {
		const response = await fetch('api/my/base/package/find_all', {
			method: 'GET',
			headers: {"Authorization": "Bearer " + $user!['JWT']}
		})
		if (response.status != 200) {
			return null
		}
		packages = await response.json();
		return packages;
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
		<div class="input-group input-group-divider grid-cols-[1fr_auto] w-80">
			<input type="search" placeholder="package" bind:value={add_package}/>
			<button class="variant-filled" on:click={async() => {
				const response = await fetch('api/my/base/package/add', {
					method: "POST",
					headers: {"Authorization": "Bearer " + $user.JWT, "Content-Type": "application/json"},
					body: JSON.stringify({"name": `${$user.username}_${add_package}`})
				})
				const obj = await response.json();
				if (response.ok) {
					toastStore.trigger({message: "Package succesfully created"})
					packages.push(obj)
					handler_init();
				} else {
					toastStore.trigger({message: obj.error});
				}
			}}>add</button>
		</div>
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
				<th on:click={() => handler.sort('namespace')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'namespace'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					namespace
				</th>
				<th on:click={() => handler.sort('actions')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'actions'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					actions
				</th>
				<th class="table-cell-fit">
					opt
				</th>
				{/if}
			</tr>
		</thead>
		<tbody>
			{#if rows}
			{#each $rows as pack}
				<tr>
					<td>{pack.name}</td>
					<td>{pack.namespace}</td>
					<td>
						{#await fetch('api/my/base/package/find?name=' + pack.name, {
							method: 'GET', headers: {'Authorization': `Bearer ${$user['JWT']}`}
						})}
							<p>fetching actions...</p>
						{:then data} 
							{#await data.json()}
							<p>loading data...</p>
							{:then obj}
								{#each obj.actions as action}
								{action.name}<br>
								{/each}
							{/await}
						{/await}
					</td>
					<td>
						<!-- svelte-ignore missing-declaration -->
						<button class="btn btn-sm variant-ringed" on:click={async () => {
							const conf = confirm('Delete ' + pack.name + "?");
								if (conf) {
									const response = await fetch(`/api/my/base/package/delete?name=${pack.name}`, {
										method: 'DELETE',
										headers: {"Authorization": "Bearer " + $user['JWT']}
									})
									if (response.ok) {
										toastStore.trigger(delete_ok);
										const index = packages.indexOf(pack);
										packages.splice(index, 1);
										handler_init();
									} else {
										toastStore.trigger(delete_failure);
									}
								}
						}}>Delete</button>
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
				<b>{$rowCount.end}</b>
				<b>{$rowCount.total}</b>
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
		<!-- <section class="lg:hidden">
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
		</section> -->
    </footer>
</div>