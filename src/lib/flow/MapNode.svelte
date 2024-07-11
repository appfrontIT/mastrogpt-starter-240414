<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';
    import { status } from '../../store';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    
    let key;
    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="key" style="top: 100px;" {isConnectable} class="handle"/>
<Handle type="target" position={Position.Left} id="value" style="top: 40px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-orange-500">Map</div>
<hr />
<span class="label">key</span>
<input class="input rounded-sm text-xs" bind:value={key} />
<span class="label">value</span>
<textarea
    rows="4"
    bind:value={data.text}
    on:input={(evt) => updateNodeData(id, { text: evt.currentTarget.value })}
    placeholder="text area"
    class="nodrag textarea rounded-sm text-xs"
    />
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
    :global(.svelte-flow__node-map) {
        width: 150px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>