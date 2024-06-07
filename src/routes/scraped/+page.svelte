<script lang="ts">
    import { TreeView, TreeViewItem, RecursiveTreeView, type TreeViewNode } from '@skeletonlabs/skeleton';
    import { clipboard } from '@skeletonlabs/skeleton';
    /** @type {import('./$types').PageData} */
	export let data;

    const collections = data.data;
    const user = data.user;
</script>

<TreeView>
    {#each collections as coll}
        <TreeViewItem>
            {coll.domain}
            <svelte:fragment slot="children">
            {#each coll.data as el}
                <TreeViewItem>
                    <div>
                        {el.url}
                    <button class="btn" use:clipboard={el.url}>Copy</button>
                    </div>
                    <svelte:fragment slot="children">
                        <TreeViewItem>
                            text
                            <button class="btn" use:clipboard={el.text}>Copy</button>
                            <svelte:fragment slot="children">
                                {el.text}
                            </svelte:fragment>
                        </TreeViewItem>
                        <TreeViewItem>
                            summary
                            <button class="btn" use:clipboard={el.summary}>Copy</button>
                            <svelte:fragment slot="children">
                                {el.summary}
                            </svelte:fragment>
                        </TreeViewItem>
                        {#if 'embedding' in el}
                        <TreeViewItem>
                            embedding
                            <button class="btn" use:clipboard={el.embedding}>Copy</button>
                            <svelte:fragment slot="children">
                                {el.embedding}
                            </svelte:fragment>
                        </TreeViewItem>
                        {/if}
                    </svelte:fragment>
                </TreeViewItem>
            {/each}
            </svelte:fragment>
        </TreeViewItem>
    {/each}
</TreeView>