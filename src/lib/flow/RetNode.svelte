<script lang="ts">
    import { Handle, Position, useHandleConnections, useNodesData, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';


    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];

    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="left-a" {isConnectable} class="handle"/>
<div class="container">
    <p class="h4 text-orange-500 py-1">return</p>
</div>
<style>
    :global(.svelte-flow__node-return) {
        width: 100px;
        height: 40px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
