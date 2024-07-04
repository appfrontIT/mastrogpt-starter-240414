<script lang="ts">
    import { Handle, Position, useHandleConnections, type NodeProps } from '@xyflow/svelte';
    import { nodes, edges } from '../../store';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];

    const connections = useHandleConnections({ nodeId: id, type: 'target' });

    // $: isConnectable = $connections.length === 0;

    // BUTTON ON TOP TO HIDE THE REST OF THE CARD
</script>

<Handle type="target" position={Position.Left} style="background: #555;" {isConnectable} />
<Handle type="target" position={Position.Left} style="background: #555; bottom: 45px; top: auto;" {isConnectable} />
<div class="container space-y-4">
<div class="h4 text-orange-500">AI node</div>
<hr />
<div id="show">
<label class="label mx-3 rounded-sm text-left">
	<span>Model:</span>
	<select class="select variant-ringed border-1 rounded-sm">
		<option value="1">gpt-3.5-turbo</option>
		<option value="2">gpt-4o</option>
	</select>
</label>
<button class="nodrag variant-ringed w-full">Prompt</button>
<button class="nodrag variant-ringed w-full" on:click={() => {
    for (let i = 0; i < $nodes.length; i++) {
        console.log($nodes[i])
        if ($nodes[i].id === id) {
            const index = $nodes.indexOf($nodes[i]);
            $nodes.splice(index, 1);
            $nodes = $nodes
        }
    }
}}>delete</button>
</div>
</div>
    <Handle
    type="source"
    position={Position.Right}
    id="a"
    style="background: orange; top: 20px; border: 50px;"
    {isConnectable}
    />

<style>
    :global(.svelte-flow__node-bot) {
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
    :global(.svelte-flow__node.selected) {
        outline: none;
        border-color: #ab02bb;
        box-shadow: 0 0 8px #ab02bb;   
    }
</style>
