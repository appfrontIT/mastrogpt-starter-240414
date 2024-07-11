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
<Handle type="target" position={Position.Left} id="left-a" style="top: 10px;" {isConnectable} class="handle"/>
<Handle type="target" position={Position.Left} id="left-b" style="top: 30px;" {isConnectable} class="handle"/>
<div class="container">
    <p class="h4 text-orange-500 py-1">!=</p>
</div>
<Handle
    type="source"
    position={Position.Right}
    id="out"
    {isConnectable}
    class="handle"
/>
<style>
    :global(.svelte-flow__node-notEqual) {
        width: 40px;
        height: 40px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
