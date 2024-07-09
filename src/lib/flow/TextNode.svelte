<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    // $: isConnectable = $connections.length === 0;

    // BUTTON ON TOP TO HIDE THE REST OF THE CARD
    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="left-a" style="top: 40px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-orange-500">Text Node</div>
<hr />
<div class="label">text</div>
<div>
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
    :global(.svelte-flow__node-text) {
        width: 200px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
