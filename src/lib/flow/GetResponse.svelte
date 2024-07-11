<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';
    import { status } from '../../store';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];

    const { updateNodeData } = useSvelteFlow();

    $$restProps;
</script>
<Handle type="source" position={Position.Right} id="status" style="top: 40px;" {isConnectable} class="handle"/>
<Handle type="source" position={Position.Right} id="headers" style="top: 65px;" {isConnectable} class="handle"/>
<Handle type="source" position={Position.Right} id="body" style="top: 90px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-violet-500">getResponse</div>
<hr />
<span class="label">status</span>
<hr />
<span class="label">headers</span>
<hr />
<span class="label">body</span>
<hr />
<div class="grid grid-cols-2">
    <button class="nodrag w-full text-left px-2">&#60;</button>
    <button class="nodrag w-full text-right px-2">	&#62;</button>
    <Handle type="source" position={Position.Right} id="out" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
    <Handle type="target" position={Position.Left} id="in" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
</div>
</div>
<style>
    :global(.svelte-flow__node-getResponse) {
        width: 150px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
