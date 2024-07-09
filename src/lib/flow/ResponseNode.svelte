<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';
    import { status } from '../../store';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    
    let body = [{'key': '', 'value': ''}]
    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="left-a" style="top: 100px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-orange-500">Response</div>
<hr />
<span class="label">status</span>
<select class="select rounded-sm text-xs">
    {#each $status as s}
        <option value={s}>{s}</option>
    {/each}
</select>
<div>
    <span>body</span>
    <textarea
    rows="4"
    bind:value={data.text}
    on:input={(evt) => updateNodeData(id, { text: evt.currentTarget.value })}
    placeholder="text area"
    class="nodrag textarea rounded-sm text-xs"
    />
</div>
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
    :global(.svelte-flow__node-response) {
        width: 200px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
