<script lang="ts">
    import { onMount } from "svelte";
	import Carousel from 'svelte-carousel'
	import { templates } from "../store";

	let carousel; // for calling methods of the carousel instance
	let curr_page = 0;

    onMount(() => {
    })

</script>
<div class="w-9/12 mx-auto space-y-4 space-x-4">
	<p class="h2">{$templates[curr_page].name}</p>
<Carousel
bind:this={carousel}
on:pageChange={ event => curr_page = event.detail }
>
	{#each $templates as {img, demo}, i}
            <img
            class="rounded-container-token hover:brightness-125"
            src={img}
            alt={img}
            title={img}
            loading="lazy"
        />
		{/each}
</Carousel>
<button class="btn variant-filled" on:click={() => {window.open($templates[curr_page].demo, '_blank')}}>demo</button>
<button class="btn variant-filled">choose</button>
</div>