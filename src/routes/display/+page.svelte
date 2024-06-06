<script lang="ts">

    /** @type {import('./$types').PageData} */
	export let data;

    let pages = data.data;
    let user = data.user;

</script>

<nav class="list-nav">
	<ul>
        {#each pages as page}
        <li>
            <a href={'https://gporchia.nuvolaris.dev/' + user.username + '/' + page} target="_blank">{page}</a>
        </li>
        {/each}
	</ul>
</nav>
