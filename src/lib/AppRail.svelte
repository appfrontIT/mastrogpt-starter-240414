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
		<AppRailAnchor href="/" on:click={() => {$selector = 0}}><img alt="menu img" src={menu_svg} class="px-1"/></AppRailAnchor>
	</svelte:fragment>
	<!-- --- -->
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 1}} name="Lookinglass" value={1} title="Lookinglass">
		<svelte:fragment slot="lead" ><img alt="manual img" src={manual_svg} class="px-1"/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 2}} name="Coder" value={2} title="Coder">
		<svelte:fragment slot="lead"><img alt="coder img" src={code_svg} class="px-1"/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 3}} name="Admin" value={3} title="Admin">
		<svelte:fragment slot="lead"><img alt="admin img" src={admin_svg} class="px-1"/></svelte:fragment>
	</AppRailTile>
    <AppRailTile bind:group={$selector} on:click={() => {$selector = 4}} name="Website" value={4} title="Website">
		<svelte:fragment slot="lead"><img alt="website img" src={website_svg} class="px-1"/></svelte:fragment>
	</AppRailTile>
    <AppRailTile bind:group={$selector} on:click={() => {$selector = 5}} name="Graph" value={5} title="Graph">
		<svelte:fragment slot="lead"><img alt="website img" src={chart_svg} class="px-1"/></svelte:fragment>
	</AppRailTile>
	<AppRailTile bind:group={$selector} on:click={() => {$selector = 6}} name="Visual devel" value={6} title="Visual devel">
		<svelte:fragment slot="lead"><img alt="website img" src={create_svg} class="px-1"/></svelte:fragment>
	</AppRailTile>
	<!-- --- -->
	<svelte:fragment slot="trail">
		<AppRailAnchor href="https://github.com/appfrontIT/mastrogpt-starter-240414" target="_blank" title="Account"><div class="px-4"><img alt="website img" src={github_svg}/></div></AppRailAnchor>
	</svelte:fragment>
</AppRail>