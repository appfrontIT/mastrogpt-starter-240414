<script lang="ts">
    import { AppRail, AppRailTile, AppRailAnchor } from '@skeletonlabs/skeleton';
    import manual_svg from '$lib/assets/manual.svg';
	import code_svg from '$lib/assets/coding.svg';
	import admin_svg from '$lib/assets/admin.svg';
	import website_svg from '$lib/assets/website.svg';
	import chart_svg from '$lib/assets/chart.svg';
    import menu_svg from '$lib/assets/menu.svg';
    import github_svg from '$lib/assets/github-mark-white.svg'
	import create_svg from '$lib/assets/create.svg'
    import { selector } from '../store'
</script>
<AppRail>
	<svelte:fragment slot="lead">
		<AppRailAnchor href="/" on:click={() => {$selector = -1}}><img alt="menu img" src={menu_svg}/></AppRailAnchor>
	</svelte:fragment>
	<!-- --- -->
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 1}} name="Lookinglass" value={1} title="Lookinglass">
		<svelte:fragment slot="lead" ><img alt="manual img" src={manual_svg}/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 2}} name="Coder" value={2} title="Coder">
		<svelte:fragment slot="lead"><img alt="coder img" src={code_svg}/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 3}} name="Admin" value={3} title="Admin">
		<svelte:fragment slot="lead"><img alt="admin img" src={admin_svg}/></svelte:fragment>
	</AppRailTile>
    <AppRailTile bind:group={$selector} on:click={() => {$selector = 4}} name="Website" value={4} title="Website">
		<svelte:fragment slot="lead"><img alt="website img" src={website_svg}/></svelte:fragment>
	</AppRailTile>
    <AppRailTile bind:group={$selector} on:click={() => {$selector = 5}} name="Graph" value={5} title="Graph">
		<svelte:fragment slot="lead"><img alt="website img" src={chart_svg}/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 6}} name="Visual devel" value={6} title="Visual devel">
		<svelte:fragment slot="lead"><img alt="website img" src={create_svg}/></svelte:fragment>
	</AppRailTile>
	<!-- --- -->
	<svelte:fragment slot="trail">
		<AppRailAnchor href="/" target="_blank" title="Account"><img alt="website img" src={github_svg}/></AppRailAnchor>
	</svelte:fragment>
</AppRail>