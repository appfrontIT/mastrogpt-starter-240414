<script lang="ts">
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
      on:dragstart={(event) => onDragStart(event, 'input')}
      draggable={true}
    >
      Input Node
    </div>
    <div
      class="btn variant-filled"
      on:dragstart={(event) => onDragStart(event, 'default')}
      draggable={true}
    >
      Default Node
    </div>
    <div
      class="btn variant-filled"
      on:dragstart={(event) => onDragStart(event, 'output')}
      draggable={true}
    >
      Output Node
    </div>
  </div>
</aside>

<style>
</style>