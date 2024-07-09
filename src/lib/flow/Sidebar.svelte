<script lang="ts">
  import BotNode from "./BotNode.svelte";
  import TextNode from "./TextNode.svelte";
  import type { NodeTypes } from "@xyflow/svelte";
  import AddNode from "./AddNode.svelte";
  import RetNode from "./RetNode.svelte";
  import ResponseNode from "./ResponseNode.svelte";

  const nodeTypes: NodeTypes = {
    bot: BotNode,
    text: TextNode,
    op: AddNode,
    return: RetNode,
    response: ResponseNode,
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
    <div
      class="btn variant-filled"
      on:dragstart={(event) => onDragStart(event, 'bot')}
      draggable={true}
    >
      AI BOT
    </div>
    <div
      class="btn variant-filled"
      on:dragstart={(event) => onDragStart(event, 'text')}
      draggable={true}
    >
      Text node
    </div>
    <div
      class="btn variant-filled"
      on:dragstart={(event) => onDragStart(event, 'op')}
      draggable={true}
    >
      +
    </div>
    <div
    class="btn variant-filled"
    on:dragstart={(event) => onDragStart(event, 'return')}
    draggable={true}
  >
    return
  </div>
  <div
    class="btn variant-filled"
    on:dragstart={(event) => onDragStart(event, 'response')}
    draggable={true}
  >
    response
  </div>
  </div>
</aside>

<style>
</style>