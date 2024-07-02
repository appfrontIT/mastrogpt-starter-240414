<script lang="ts">
    import { Handle, Position, type NodeProps } from '@xyflow/svelte';

    type $$Props = NodeProps;
    export let id: $$Props['id'];
    export let isConnectable: $$Props['isConnectable'];
</script>

<Handle type="target" position={Position.Left} style="background: #555;" {isConnectable} />
<div>Custom node</div>
<button class="nodrag">delete</button>
    <Handle
    type="source"
    position={Position.Right}
    id="a"
    style="background: #555;"
    {isConnectable}
    />

<style>
    :global(.svelte-flow__node-selectorNode) {
        font-size: 12px;
        background: #eee;
        border: 1px solid #555;
        border-radius: 5px;
        text-align: center;
    }
</style>
