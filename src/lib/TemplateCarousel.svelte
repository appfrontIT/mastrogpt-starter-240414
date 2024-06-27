<script lang="ts">
    import { onMount } from "svelte";

    const modules = import.meta.glob("./templates/*", { eager: true });
    const pages = Object.keys(modules).map((key) => modules[key].default);
    let templates = new Array();
    let elemMovies: HTMLDivElement;

    onMount(() => {
    })

    function multiColumnLeft(): void {
        let x = elemMovies.scrollWidth;
        if (elemMovies.scrollLeft !== 0) x = elemMovies.scrollLeft - elemMovies.clientWidth;
        elemMovies.scroll(x, 0);
    }

    function multiColumnRight(): void {
        let x = 0;
    	// -1 is used because different browsers use different methods to round scrollWidth pixels.
        if (elemMovies.scrollLeft < elemMovies.scrollWidth - elemMovies.clientWidth - 1) x = elemMovies.scrollLeft + elemMovies.clientWidth;
        elemMovies.scroll(x, 0);
    }
</script>

<div class="grid grid-cols-[auto_1fr_auto] gap-4 items-center">
    <!-- {console.log(templates)}
    {console.log(templates.length)} -->
	
	<button type="button" class="btn-icon variant-filled" on:click={multiColumnLeft}>
		<i class="fa-solid fa-arrow-left" />
	</button>
	
	<div bind:this={elemMovies} class="snap-x snap-mandatory scroll-smooth flex gap-2 pb-2 overflow-x-auto">
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
	
	<button type="button" class="btn-icon variant-filled" on:click={multiColumnRight}>
		<i class="fa-solid fa-arrow-right" />
	</button>
</div>