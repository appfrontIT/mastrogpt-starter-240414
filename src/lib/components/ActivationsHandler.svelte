<script lang='ts'>
	import { user, chat_room, selector, activation_name, status } from '../../store'
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
		handler = new DataHandler(actions!, {rowsPerPage: 10});
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
		await get_activations();
		handler_init();
	})

	async function get_activations() {
		let response: Response;
		console.log($activation_name)
		if ($activation_name) {
			response = await fetch('api/my/base/action/activations?name=' + $activation_name, {
				method: "GET",
				headers: {"Authorization": "Bearer " + $user['JWT']},
			})
			$activation_name = null;
		} else {
			response = await fetch('api/my/base/action/activations', {
				method: 'GET',
				headers: {"Authorization": "Bearer " + $user!['JWT']}
			})
		}
		if (response.status != 200) {
			return null
		}
		actions = await response.json();
		return actions;
	}

	$: actions = actions;
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
		<button class="btn variant-filled" on:click={async () => {
			await get_activations();
			handler_init();
		}}>refresh</button>
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
				<th on:click={() => handler.sort('activationId')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'activationId'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					activationId
				</th>
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
				<th on:click={() => handler.sort('duration')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'duration'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					duration
				</th>
				<th on:click={() => handler.sort('start')} class="cursor-pointer select-none">
					<div class="flex h-full items-center justify-start gap-x-2">
						<slot />
						{#if $sorted.identifier === 'start'}
							{#if $sorted.direction === 'asc'}
								&darr;
							{:else if $sorted.direction === 'desc'}
								&uarr;
							{/if}
						{:else}
							&updownarrow;
						{/if}
					</div>
					start
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
					<td><button class="btn sm" on:click={async() => {
						const response = await fetch('api/my/base/action/activation?id=' + pack.activationId, {
							method: "GET",
							headers: {"Authorization": "Bearer " + $user['JWT']},
						})
						if (response.ok) {
							const obj = await response.json();
							modalStore.trigger({
								type: 'component',
								component: 'modalActivation',
								meta: { info: obj }
							})
						}
					}}>{pack.activationId}</button></td>
					<td>{pack.annotations[0].value.split('/')[1] + "/" + pack.annotations[0].value.split('/')[2]}</td>
					<td>{pack.duration}</td>
					<td>{new Date(pack.start).toLocaleString()}</td>
					<td>
						<button class="btn-icon hover:variant-filled" use:popup={{event: 'click', target: 'action_opt_' + i, placement: 'left'}}><p class="h3">⋮</p></button>
					</td>
				<div data-popup='action_opt_{i}'>
					<div class="btn-group-vertical variant-filled">
					<button on:click={async() => {
						// modalStore.trigger({type: 'component', component: 'modalWaiting', meta: { msg: "Preparing the editor..." }});
						const r = await fetch(`api/my/base/action/find?name=${pack.name}&package=${pack.annotations[0].value.split('/')[1]}`, {
							method: "GET",
							headers: {"Authorization": "Bearer " + $user['JWT']}
						})
						console.log(r.status)
						if (r.ok) {
							const obj = await r.json();
							$chat_room[2].editor.name = obj.name;
							$chat_room[2].editor.package = obj.namespace.split('/')[1];
							$chat_room[2].editor.function = obj.exec.code;
							for (let i = 0; i < obj.annotations.length; i++) {
								if (obj.annotations[i].key === "description") {
									$chat_room[2].editor.description = obj.annotations[i].value;
									break;
								}
							}
							$chat_room[2].editor.language = obj.exec.kind.split(':')[0];
							if ($chat_room[2].editor.language === 'nodejs') $chat_room[2].editor.language = 'javascript';
							modalStore.close();
							$selector = 2;
							return;
						}
						modalStore.close();
						return null;
					}}>edit</button>
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