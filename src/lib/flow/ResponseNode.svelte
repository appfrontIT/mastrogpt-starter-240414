<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';
    import { status } from '../../store';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    
    let body = [{'key': '', 'value': ''}]
    let headers = [{'key': '', 'value': ''}]
    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="headers" style="top: 100px;" {isConnectable} class="handle"/>
<Handle type="target" position={Position.Left} id="body" style="bottom: 30px; top: auto;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-violet-500">Return</div>
<hr />
<span class="label">status</span>
<select class="select rounded-sm text-xs">
    {#each $status as s}
        <option value={s}>{s}</option>
    {/each}
</select>
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
}}>Remove</button><br><hr />
<span>body</span>
<hr />
<div class="grid grid-cols-2">
    <button class="nodrag w-full text-left px-2">&#60;</button>
    <Handle type="target" position={Position.Left} id="in" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
</div>
</div>
<style>
    :global(.svelte-flow__node-response) {
        width: 200px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
