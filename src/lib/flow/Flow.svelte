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
    type ColorMode
  } from '@xyflow/svelte';
    import { getModeOsPrefers, getModeUserPrefers, getModeAutoPrefers } from '@skeletonlabs/skeleton';
    import '@xyflow/svelte/dist/style.css';
    import Sidebar from './Sidebar.svelte';
    import CustomNode from './CustomNode.svelte';

    const { screenToFlowPosition } = useSvelteFlow();
    const nodeTypes = {selectorNode: CustomNode};
    const edges = writable([]);
    const nodes = writable([
    {
      id: '1',
      type: 'input',
      data: { label: 'Input Node' },
      position: { x: 150, y: 5 }
    },
    {
      id: '2',
      type: 'default',
      data: { label: 'Default Node' },
      position: { x: 0, y: 150 }
    },
    {
      id: '3',
      type: 'output',
      data: { label: 'Output Node' },
      position: { x: 300, y: 150 }
    }
  ]);
    let colorMode: ColorMode = getModeUserPrefers() ? 'light' : 'dark';

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
                type: 'selectorNode',
                position,
                data: { label: `${type} node` },
                origin: [0.5, 0.0]
            } satisfies Node;
            $nodes.push(newNode);
            $nodes = $nodes;
            };
</script>

<main>
    <div class="grid grid-rows-[1fr_auto] h-full">
        <SvelteFlow {nodes} {edges} {colorMode} {nodeTypes} fitView on:dragover={onDragOver} on:drop={onDrop}>
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

<style>
    main {
    height: 87vh;
    }
</style>