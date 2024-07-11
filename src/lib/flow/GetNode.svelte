<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    let input: string;
    // $: isConnectable = $connections.length === 0;

    // BUTTON ON TOP TO HIDE THE REST OF THE CARD
    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="left-a" style="top: 15px;" {isConnectable} class="handle"/>
<div class="container">
<div class="text-orange-500">get</div>
<input class="input rounded-sm text-xs" type="text" bind:value={input} />
</div>
<Handle
    type="source"
    position={Position.Right}
    id="out"
    style="top: 15px;"
    {isConnectable}
    class="handle"
/>
<style>
    :global(.svelte-flow__node-get) {
        width: 100px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
