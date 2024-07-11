<script lang="ts">
  import BotNode from "./BotNode.svelte";
  import TextNode from "./TextNode.svelte";
  import type { NodeTypes } from "@xyflow/svelte";
  import AddNode from "./AddNode.svelte";
  import ResponseNode from "./ResponseNode.svelte";
  import MapNode from "./MapNode.svelte";
  import RequestNode from "./RequestNode.svelte";
  import EqualNode from "./EqualNode.svelte";
  import GetResponse from "./GetResponse.svelte";
  import IfNode from "./IfNode.svelte";
  import NumberNode from "./NumberNode.svelte";
  import StartNode from "./StartNode.svelte";
  import GetNode from "./GetNode.svelte";

  const nodeTypes: NodeTypes = {
    bot: BotNode,
    text: TextNode,
    op: AddNode,
    response: ResponseNode,
    request: RequestNode,
    map: MapNode,
    equal: EqualNode,
    getResponse: GetResponse,
    if: IfNode,
    number: NumberNode,
    start: StartNode,
    get: GetNode
  };
  const onDragStart = (event: DragEvent, nodeType: string) => {
    if (!event.dataTransfer) {
      return null;
    }

    event.dataTransfer.setData('application/svelteflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };
</script>

<aside>
  <div class="flex space-x-4 justify-center">
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'start')} draggable={true}>
      start
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'bot')} draggable={true}>
      AI BOT
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'text')} draggable={true}>
      Text node
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'op')} draggable={true}>
      +
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'response')} draggable={true}>
      return
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'request')} draggable={true}>
      request
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'map')} draggable={true}>
      map
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'equal')} draggable={true}>
      ==?
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'getResponse')} draggable={true}>
      getResponse
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'if')} draggable={true}>
      if
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'number')} draggable={true}>
      number
    </div>
    <div class="btn variant-filled" on:dragstart={(event) => onDragStart(event, 'get')} draggable={true}>
      get
    </div>
  </div>
</aside>

<style>
</style>