<script lang="ts">
    import { onMount } from "svelte";

    const modules = import.meta.glob("./templates/*", { eager: true });
    const pages = Object.keys(modules).map((key) => modules[key].default);

    let elemCarousel: HTMLDivElement;

    onMount(() => {
    })

    function multiColumnLeft(): void {
	let x = elemCarousel.scrollWidth;
	if (elemCarousel.scrollLeft !== 0) x = elemCarousel.scrollLeft - elemCarousel.clientWidth;
	elemCarousel.scroll(x, 0);
}

function multiColumnRight(): void {
	let x = 0;
	// -1 is used because different browsers use different methods to round scrollWidth pixels.
	if (elemCarousel.scrollLeft < elemCarousel.scrollWidth - elemCarousel.clientWidth - 1) x = elemCarousel.scrollLeft + elemCarousel.clientWidth;
	elemCarousel.scroll(x, 0);
}
</script>

<div class="grid grid-cols-[auto_1fr_auto] gap-4 items-center">
	
	<button type="button" class="btn-icon variant-ringed" on:click={multiColumnLeft}>
		<i class="fa-solid fa-arrow-left" />
	</button>
	
	<div bind:this={elemCarousel} class="snap-x snap-mandatory scroll-smooth flex gap-2 pb-2 overflow-x-auto">
        
        {#each pages as img, i}
            <img
            class="rounded-container-token hover:brightness-125"
            src={img}
            alt={img}
            title={img}
            loading="lazy"
        />
		{/each}
	</div>
	
	<button type="button" class="btn-icon variant-ringed" on:click={multiColumnRight}>
		<i class="fa-solid fa-arrow-right" />
	</button>
</div>