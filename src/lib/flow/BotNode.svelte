<script lang="ts">
    import { Handle, Position, useNodesData, useHandleConnections, type NodeProps, useSvelteFlow } from '@xyflow/svelte';

    type $$Props = NodeProps;

    export let data: $$Props['data'];
    export let temp: $$Props['data']['temp'] = 0;
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];

    const prompt_connections = useHandleConnections({
        nodeId: id,
        type: 'target',
        id: 'prompt_handle'
    });
    const query_connections = useHandleConnections({
        nodeId: id,
        type: 'target',
        id: 'query_handle'
    });

    const { updateNodeData } = useSvelteFlow();

    $: promptNodesData = useNodesData($prompt_connections[0]?.source);
    $: queryNodesData = useNodesData($query_connections[0]?.source);

    $: data.prompt = $promptNodesData?.data?.text;
    $: data.query = $queryNodesData?.data?.text;

    $$restProps;
</script>
<Handle type="target" position={Position.Left} id="query_handle" style="top: 285px;" {isConnectable} class="handle"/>
<Handle type="target" position={Position.Left} id="prompt_handle" style="top: 175px;" {isConnectable} class="handle"/>
<Handle type="target" position={Position.Left} id="tools_handle" style="top: 100px;" {isConnectable} class="handle"/>
<div class="container">
<div class="h4 text-violet-500">AI node</div>
<hr />
<div id="show">
    <span>Model</span>
    <label class="nodrag label rounded-sm text-left">
        <select class="select variant-ringed border-1 rounded-sm text-center text-xs">
            <option value="1">gpt-3.5-turbo</option>
            <option value="2">gpt-4o</option>
        </select>
    </label>
    <span>Tools</span><hr />
    <span>Temperature {temp / 10}</span>
    <input type="range" id="temperature" class="input rounded-sm text-xs nodrag" max="20" min="0" bind:value={temp}/>
    <hr />
<p>prompt</p>
<hr />
    <textarea
    id="prompt"
    rows="4"
    bind:value={data.prompt}
    on:input={(evt) => updateNodeData(id, { text: evt.currentTarget.value })}
    placeholder="prompt area"
    class="nodrag textarea rounded-sm text-xs"
    />
<p>query</p>
<hr />
    <textarea
    rows="4"
    bind:value={data.query}
    on:input={(evt) => updateNodeData(id, { text: evt.currentTarget.value })}
    placeholder="prompt area"
    class="nodrag textarea rounded-sm text-xs"
    />
<!-- <button class="nodrag variant-ringed w-full" on:click={() => {
    for (let i = 0; i < $nodes.length; i++) {
        console.log($nodes[i])
        if ($nodes[i].id === id) {
            const index = $nodes.indexOf($nodes[i]);
            $nodes.splice(index, 1);
            $nodes = $nodes
        }
    }
}}>delete</button> -->
<div class="grid grid-cols-2">
    <button class="nodrag w-full text-left px-2">&#60;</button>
    <button class="nodrag w-full text-right px-2">	&#62;</button>
    <Handle type="source" position={Position.Right} id="out" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
    <Handle type="target" position={Position.Left} id="in" style="bottom: 5px; top: auto; background-color: rgb(139 92 246);" {isConnectable} class="handle"/>
</div>
</div>
</div>

<style>
    :global(.svelte-flow__node-bot) {
        width: 200px;
        font-size: 12px;
        background: #000000;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
