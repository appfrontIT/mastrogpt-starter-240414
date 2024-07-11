<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';
    import { status } from '../../store';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    
    const { updateNodeData } = useSvelteFlow();
    let url: string;
    let headers = [{'key': '', 'value': ''}]

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="left-a" style="top: 100px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-orange-500">Request</div>
<hr />
<span class="label">url</span>
<input class="input rounded-sm text-xs" bind:value={url} />
<span class="label">headers</span>
{#each headers as v, i}
	<input class="input rounded-sm text-xs" id={i} type="text" bind:value={headers[i].key} placeholder="key"/>
    <br>
	<input class="input rounded-sm text-xs" id={i} type="text" bind:value={headers[i].value} placeholder="value"/>
{/each}
<button class="btn rounded-sm text-xs" on:click|preventDefault={() => {
    headers = [...headers, {key: '', value: ''}]
}}>Add</button><span class="divider-vertical h-1" />
<button class="btn rounded-sm text-xs" on:click={() => {
    if (headers.length == 1) { return ;}
    headers = headers.slice(0, headers.length - 1);
}}>Remove</button>
<hr />
    <span>body</span>
<hr />
<button class="nodrag w-full text-right px-2">></button>
</div>
<Handle
    type="source"
    position={Position.Right}
    id="out"
    style="bottom: 5px; top: auto;"
    {isConnectable}
    class="handle"
/>
<style>
    :global(.svelte-flow__node-request) {
        width: 200px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
