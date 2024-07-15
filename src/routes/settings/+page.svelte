<script lang="ts">
    import { Avatar } from "@skeletonlabs/skeleton";
    import { user } from "../../store";
    import { onMount } from "svelte";

    async function get_user() {
		const res = await fetch('api/my/base/auth/user', {
                method: 'GET',
                credentials: 'include'
            })
		if (res.ok) { const obj = await res.json(); $user = obj; return obj; }
		else { throw new Error('failed to get user') };
	}

    onMount(async () => {
        await get_user();
    })
</script>

<div class="grid grid-cols-5">
    <div class="place-self-center">
        {#if $user}
        <Avatar
				initials={$user.username[0]}
				border="border-2 border-surface-300-600-token hover:!border-primary-500"
				cursor="cursor-pointer"
                width="w-48"
			/>
        {/if}
    </div>
    <div class="col-span-2 mx-16 my-8 space-y-4">
        <label class="label">
            <span>name</span>
            <input class="input" type="text" bind:value={$user.name}/>
        </label>
        <label class="label">
            <span>surname</span>
            <input class="input" type="text" bind:value={$user.surname}/>
        </label>
        <label class="label">
            <span>username</span>
            <input class="input" type="text" bind:value={$user.username}/>
        </label>
        <label class="label">
            <span>email</span>
            <input class="input" type="text" bind:value={$user.email}/>
        </label>
        <label class="label">
            <span>namespace</span>
            <input class="input" type="text" bind:value={$user.namespace} readonly>
        </label>
        <label class="label">
            <span>role</span>
            <input class="input" type="text" bind:value={$user.role} readonly>
        </label>
    </div>
    <div class="col-span-2 mx-16 my-8 space-y-4">
        <label class="label">
            <span>mobile number</span>
            <input class="input" type="text" bind:value={$user.mobile}>
        </label>
        <label class="label">
            <span>address</span>
            <input class="input" type="text" bind:value={$user.address}>
        </label>
        <label class="label">
            <span>postal code</span>
            <input class="input" type="text" bind:value={$user.postcode}>
        </label>
        <label class="label">
            <span>state</span>
            <input class="input" type="text" bind:value={$user.state}>
        </label>
    </div>
</div>
<div class="grid grid-cols-3">
    <button class="btn variant-filled col-start-2 mx-40" on:click={async () => {
        const response = await fetch('api/my/base/user/update', {
            method: "PUT",
            headers: {"Content-Type": "application/json", "Authorization": "Bearer " + $user.JWT},
            body: JSON.stringify({ 'data': {
                "name": $user.name,
                "surname": $user.surname,
                "username": $user.username,
                "email": $user.email,
                "mobile": $user.mobile,
                "address": $user.address,
                "postcode": $user.postcode,
                "state": $user.state,
                },
                "id": $user._id
            })
        })
        if (response.ok) { alert('user updated'); return;}
        else {alert("there was an error while updating the user"); return;}
    }}>update</button>
</div>