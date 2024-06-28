<script lang="ts">
    import { AppRail, AppRailTile, AppRailAnchor } from '@skeletonlabs/skeleton';
    import manual_svg from '$lib/manual.svg';
	import code_svg from '$lib/coding.svg';
	import admin_svg from '$lib/admin.svg';
	import website_svg from '$lib/website.svg';
	import chart_svg from '$lib/chart.svg';
    import menu_svg from '$lib/menu.svg';
    import github_svg from '$lib/github-mark-white.svg'
    import { selector } from '../store'

    let currentTile: number = $selector;
</script>

<AppRail width="w-16">
	<svelte:fragment slot="lead">
		<AppRailAnchor href="/" on:click={() => {$selector = -1}}><img alt="menu img" src={menu_svg}/></AppRailAnchor>
	</svelte:fragment>
	<!-- --- -->
	<AppRailTile bind:group={currentTile} on:click={() => {$selector = 1}} name="tile-1" value={0} title="tile-1">
		<svelte:fragment slot="lead" ><img alt="manual img" src={manual_svg}/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={currentTile} on:click={() => {$selector = 2}} name="tile-2" value={1} title="tile-2">
		<svelte:fragment slot="lead"><img alt="coder img" src={code_svg}/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={currentTile} on:click={() => {$selector = 3}} name="tile-3" value={2} title="tile-3">
		<svelte:fragment slot="lead"><img alt="admin img" src={admin_svg}/></svelte:fragment>
	</AppRailTile>
    <AppRailTile bind:group={currentTile} on:click={() => {$selector = 4}} name="tile-4" value={3} title="tile-4">
		<svelte:fragment slot="lead"><img alt="website img" src={website_svg}/></svelte:fragment>
	</AppRailTile>
    <AppRailTile bind:group={currentTile} on:click={() => {$selector = 5}} name="tile-5" value={4} title="tile-5">
		<svelte:fragment slot="lead"><img alt="website img" src={chart_svg}/></svelte:fragment>
	</AppRailTile>
	<!-- --- -->
	<svelte:fragment slot="trail">
		<AppRailAnchor href="/" target="_blank" title="Account"><img alt="website img" src={github_svg}/></AppRailAnchor>
	</svelte:fragment>
</AppRail>