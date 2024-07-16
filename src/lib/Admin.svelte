<script lang='ts'>
import { user } from '../store'
import { TabGroup, Tab, TabAnchor } from '@skeletonlabs/skeleton';
import { onMount, onDestroy } from 'svelte';
import { DataHandler } from '@vincjo/datatables';
import type { Readable, Writable } from 'svelte/store';
import UsersHandler from './components/UsersHandler.svelte';
import PackageHandler from './components/PackageHandler.svelte';
import ActionsHandler from './components/ActionsHandler.svelte';
import PendingHandler from './components/PendingHandler.svelte';
import ActivationsHandler from './components/ActivationsHandler.svelte';

let users: any[] | null = [];
let tabSet: number = 0;
let orderBy: string;
let value: string;
let users_handler: DataHandler<any>;
let users_rows: Readable<any[]>;
let users_sorted: Writable<{
    identifier?: string | undefined;
    direction?: "desc" | "asc" | undefined;
}>;

onMount(async () => {
	await get_users();
	users_handler = new DataHandler(users!, {rowsPerPage: 5});
	users_rows = users_handler.getRows();
	users_sorted = users_handler.getSort();
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
<div class="col-span-2 px-24">
<TabGroup justify='justify-center'>
	<Tab bind:group={tabSet} name="tab1" value={0}>Users</Tab>
	<Tab bind:group={tabSet} name="tab2" value={1}>packages</Tab>
	<Tab bind:group={tabSet} name="tab3" value={2}>Actions</Tab>
	<Tab bind:group={tabSet} name="tab4" value={3}>Activations</Tab>
	{#if $user.role == 'admin'}
	<Tab bind:group={tabSet} name="tab4" value={4}>Pendings</Tab>
	{/if}
	<!-- Tab Panels --->
	<svelte:fragment slot="panel">
		{#if tabSet === 0}
			<UsersHandler />
		{:else if tabSet === 1}
			<PackageHandler />
		{:else if tabSet === 2}
			<ActionsHandler />
		{:else if tabSet === 3}
			<ActivationsHandler />
		{:else if tabSet === 4}
			<PendingHandler />
		{/if}
	</svelte:fragment>
</TabGroup>
</div>