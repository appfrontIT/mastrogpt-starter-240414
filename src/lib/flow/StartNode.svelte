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
<Handle type="source" position={Position.Right} id="args" style="top: 40px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-violet-500">start</div>
<hr />
<div>args</div>
<hr />
<div>
    <button class="nodrag w-full text-right px-2">&#62;</button>
    <Handle type="source" position={Position.Right} id="in" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
</div>
</div>
<style>
    :global(.svelte-flow__node-start) {
        width: 200px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
