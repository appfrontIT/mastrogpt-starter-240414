<script lang="ts">
    import { Handle, Position, useHandleConnections, useNodesData, type NodeProps, type EdgeProps, useSvelteFlow } from '@xyflow/svelte';


    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
    
    const connections_1 = useHandleConnections({
        nodeId: id,
        type: 'target',
        id: 'left-a'
    });
    const connections_2 = useHandleConnections({
        nodeId: id,
        type: 'target',
        id: 'left-b'
    });

    // BUTTON ON TOP TO HIDE THE REST OF THE CARD
    const { updateNodeData } = useSvelteFlow();
    
    $: NodesData1 = useNodesData($connections_1[0]?.source);
    $: NodesData2 = useNodesData($connections_2[0]?.source);

    $$restProps;
</script>
<Handle type="source" position={Position.Right} id="true" style="top: 40px; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
<Handle type="source" position={Position.Right} id="false" style="top: 70px; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
<hr />
<div class="container">
    <div class="h4 text-orange-500">if</div><hr />
    <p class="text-right px-2">true</p>
    <p class="text-right px-2">false</p><hr />
    <div class="grid grid-cols-2">
        <button class="nodrag w-full text-left px-2">&#60;</button>
        <Handle type="target" position={Position.Left} id="in" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
    </div>
</div>
<Handle
    type="target"
    position={Position.Left}
    style="top: 15px;"
    id="cond"
    {isConnectable}
    class="handle"
/>
<style>
    :global(.svelte-flow__node-if) {
        width: 60px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
