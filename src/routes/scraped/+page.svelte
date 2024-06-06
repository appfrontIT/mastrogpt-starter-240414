<script lang="ts">
    import { TreeView, TreeViewItem, RecursiveTreeView, type TreeViewNode } from '@skeletonlabs/skeleton';
    /** @type {import('./$types').PageData} */
	export let data;

    let collections = data.data;
    let user = data.user;
</script>

<TreeView>
    {#each collections.entries() as [k, v], i}
    url: {k}
    <TreeViewItem>
		<svelte:fragment slot="children">
            {#each v as el}
            <TreeViewItem>
                url: {el.url}
                <svelte:fragment slot="children">
			<TreeViewItem>
				{el.content}
			</TreeViewItem>
			<TreeViewItem>
				{el.summary}
			</TreeViewItem>
            {#if 'embedding' in el}
            <TreeViewItem>
				{el.embedding}
			</TreeViewItem>
            {/if}
            </svelte:fragment>
            </TreeViewItem>
        {/each}
		</svelte:fragment>
	</TreeViewItem>
    {/each}
</TreeView>