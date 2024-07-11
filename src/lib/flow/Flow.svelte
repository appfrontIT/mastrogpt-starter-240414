<script lang="ts">
    import { writable } from 'svelte/store';
    import {
    SvelteFlow,
    Controls,
    Background,
    ControlButton,
    BackgroundVariant,
    MiniMap,
    useSvelteFlow,
    type Node,
    type ColorMode,
    type NodeTypes,
  } from '@xyflow/svelte';
    import { getModeOsPrefers, getModeUserPrefers, getModeAutoPrefers } from '@skeletonlabs/skeleton';
    import '@xyflow/svelte/dist/style.css';
    import Sidebar from './Sidebar.svelte';
    import BotNode from './BotNode.svelte';
    import { nodes, edges } from '../../store'
	import TextNode from './TextNode.svelte';
    import AddNode from './AddNode.svelte';
    import RetNode from './RetNode.svelte';
    import ResponseNode from './ResponseNode.svelte';
    import MapNode from './MapNode.svelte';
    import RequestNode from './RequestNode.svelte';
    import EqualNode from "./EqualNode.svelte";
    import NotEqualNode from "./NotEqualNode.svelte";

    const nodeTypes: NodeTypes = {
        bot: BotNode,
        text: TextNode,
        op: AddNode,
        return: RetNode,
        response: ResponseNode,
        request: RequestNode,
        map: MapNode,
        equal: EqualNode,
        notEqual: NotEqualNode
    };

    const { screenToFlowPosition } = useSvelteFlow();
    let colorMode: ColorMode = getModeUserPrefers() ? 'light' : 'dark';
    let selectedNode = null;
    const onDragOver = (event: DragEvent) => {
        event.preventDefault();
    
        if (event.dataTransfer) { event.dataTransfer.dropEffect = 'move';} };

        const onDrop = (event: DragEvent) => {
            event.preventDefault();
            if (!event.dataTransfer) { return null;}

            const type = event.dataTransfer.getData('application/svelteflow');

            const position = screenToFlowPosition({
                x: event.clientX,
                y: event.clientY
            });
            const newNode = {
                id: `${Math.random()}`,
                type,
                position,
                data: { label: `${type} node`, text: '', prompt: '', query: ''},
                origin: [0.5, 0.0],
                
            } satisfies Node;
            $nodes.push(newNode);
            $nodes = $nodes;
            };
</script>

<main>
    <div class="grid grid-rows-[1fr_auto] h-full">
        <SvelteFlow {nodes} {edges} {colorMode} {nodeTypes} fitView
        on:dragover={onDragOver}
        on:drop={onDrop}
        on:nodeclick={(event) => {selectedNode = event.detail.node}}
        on:paneclick={() => {selectedNode = null;}}
        >
            <Background />
            <Controls>
                <ControlButton on:click={() => console.log('⚡️')}>
                    ⚡️
                </ControlButton>
            </Controls>
        </SvelteFlow>
        <Sidebar />
</div>
</main>
<!-- <svelte:window on:keydown|preventDefault={(e) => {
  if (e.key === 'Delete' && selectedNode != null) {
    const index = $nodes.indexOf(selectedNode);
    $nodes.splice(index, 1);
    $nodes = $nodes;
  }
}} /> -->
<style>
    main {
    height: 87vh;
    }
        :global(.svelte-flow__node.selected) {
        outline: none;
        border-color: #ab02bb;
        box-shadow: 0 0 8px #ab02bb;   
    }
    :global(.svelte-flow .svelte-flow__handle) {
        border: 50px;
        background-color: orange;
    }
    /* :global(.svelte-flow .svelte-flow__handle-right) {
        right: -10px;
    } */
</style>