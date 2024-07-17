<script lang='ts'>
	import { user, editor, selector, tabSet, activation_name } from '../../store'
	import { onMount, onDestroy } from 'svelte';
	import { DataHandler } from '@vincjo/datatables';
	import type { Readable, Writable } from 'svelte/store';
	import { popup } from '@skeletonlabs/skeleton';
	import { Toast, getToastStore, getModalStore } from '@skeletonlabs/skeleton';
	import { type ModalSettings } from '@skeletonlabs/skeleton';
	import type { ToastSettings, ToastStore } from '@skeletonlabs/skeleton';

	const modalStore = getModalStore();

	let actions: any[] | null = [];
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
	const delete_ok: ToastSettings = {
		message: 'Azione eliminata con successo!',
	};
	const delete_failure: ToastSettings = {
		message: 'Un problema é accorso durante il processo di eliminazione, per favore riprovare',
	};
	
	function handler_init() {
		handler = new DataHandler(actions!, {rowsPerPage: 5});
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
		await get_actions();
		handler_init();
	})

	async function get_actions() {
		const response = await fetch('api/my/base/action/find_all', {
			method: 'GET',
			headers: {"Authorization": "Bearer " + $user!['JWT']}
		})
		if (response.status != 200) {
			return null
		}
		actions = await response.json();
		return actions;
	}
	</script>

<div class="overflow-x-auto space-y-2" style="height: 80vh;">
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
				<th on:click={() => handler.sort('annotations')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'annotations'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					annotations
				</th>
				<th on:click={() => handler.sort('url')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'url'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					url
				</th>
				<th class="table-cell-fit">
					opt
				</th>
				{/if}
			</tr>
		</thead>
		<tbody>
			{#if rows}
			{#each $rows as pack, i}
				<tr>
					<td>{pack.name}</td>
					<td>{pack.package}</td>
					<td>
                        {#each pack.annotations as ann}
                            {ann.key}: {ann.value}<br>
                        {/each}
                    </td>
					<td>
                        {pack.url}
                    </td>
					<br>
				<button class="btn-icon hover:variant-filled" use:popup={{event: 'click', target: 'action_opt_' + i, placement: 'left'}}><h3 class="h3">⋮</h3></button>
				<div data-popup='action_opt_{i}'>
					<div class="btn-group-vertical variant-filled">
					<button on:click={async() => {
						modalStore.trigger({type: 'component', component: 'modalWaiting', meta: { msg: "Preparing the editor..." }});
						const r = await fetch(`/api/my/base/action/find?name=${pack.name}&package=${pack.package}`, {
							method: "GET",
							headers: {"Authorization": "Bearer " + $user['JWT']}
						})
						if (r.ok) {
							const obj = await r.json();
							$editor.name = obj.name;
							$editor.package = obj.namespace.split('/')[1];
							$editor.function = obj.exec.code;
							for (let i = 0; i < obj.annotations.length; i++) {
								if (obj.annotations[i].key === "description") {
									$editor.description = obj.annotations[i].value;
									break;
								}
							}
							$editor.language = obj.exec.kind.split(':')[0];
							if ($editor.language === 'nodejs') $editor.language = 'javascript';
							modalStore.close();
							$selector = 2;
							return;
						}
						modalStore.close();
						return null;
					}}>edit</button>
					<button on:click={async () => {
					const response = await fetch(`api/my/base/action/activations?name=${pack.package}/${pack.name}`, {
							method: "GET",
							headers: {"Authorization": "Bearer " + $user['JWT']},
						})
						const obj = await response.json();
						$activation_name = `${pack.package}/${pack.name}`
						$tabSet = 3;
						}}>activations</button>
					<button on:click={async () => {
						const conf = confirm('Sei sicuro di voler eliminare questa azione?');
						if (conf) {
							modalStore.trigger({type: 'component', component: 'modalWaiting', meta: { msg: `deleting ${pack.name}...` }});
							const response = await fetch(`api/my/base/action/delete?name=${pack.name}&package=${pack.package}`, {
								method: 'DELETE',
								headers: {"Authorization": "Bearer " + $user['JWT']}
							})
							if (response.ok) {
								const index = actions.indexOf(pack);
								actions.splice(index, 1);
								handler_init();
								modalStore.close();
								modalStore.trigger({type: 'component', component: 'modalWaiting', meta: { msg: `removing action spec from openAPI...` }});
								const openapi_resp = await fetch(`api/my/base/openAPI/delete?action=/gporchia/${pack.package}/${pack.name}`, {
									method: 'DELETE',
									headers: {'Authorization': `Bearer ${$user['JWT']}`}
								})
								modalStore.close();
								if (openapi_resp.ok) {
									toastStore.trigger(delete_ok);
								} else {
									alert('Something went wrong while removing the action from swagger');
								}
							} else {
								modalStore.close();
								toastStore.trigger(delete_failure);
							}
						}
					}}>delete</button>
				</div>
				</div>
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