<script lang="ts">
    import CodeMirror from "svelte-codemirror-editor";
    import { javascript } from "@codemirror/lang-javascript";
    import { python } from "@codemirror/lang-python";
    import { php } from "@codemirror/lang-php";
    import { html } from "@codemirror/lang-html";
    import { go } from "@codemirror/lang-go";
    import { oneDark } from "@codemirror/theme-one-dark";
    import {EditorView, keymap} from "@codemirror/view"
    import {defaultKeymap} from "@codemirror/commands"
    import { editor } from '../store'
    import { getToastStore, popup } from '@skeletonlabs/skeleton';
    import type { SvelteComponent } from 'svelte';
    
    let view: EditorView;
    let value = "";
    let watch_toggle = false;
    let packages: string[] = [];

    export let parent: SvelteComponent;

    const toastStore = getToastStore();

    const languages_func = new Map<string, any>([
        ['go', go()],
        ['html', html()],
        ['javascript', javascript()],
        ['php', php()],
        ['python', python()],
    ]);
    const languages = ['go', 'html', 'javascript', 'php', 'python'];

    let props: CodeMirror["$$prop_def"] = {
        basic: true,
        useTab: true,
        editable: true,
        lineWrapping: false,
        readonly: false,
        tabSize: 2,
        placeholder: null,
        lang: null,
        theme: null,
        nodebounce: false
    };

    // onMount(async () => {})

</script>
<div class="grid grid-cols-12 gap-4 space-y-1 w-max" style="height: 5vh;">
    <input class="input col-span-4" title="Action name" type="text" placeholder="action name" bind:value={$editor.name}>
    {#if $editor.language != 'html'}
    <input class="input col-span-4" title="Description" type="text" placeholder="description" bind:value={$editor.description}/>
    <select class="select col-span-1" bind:value={$editor.package}>
        <option disabled selected value>Package</option>
        {#each packages as pack}
            <option value={pack}>{pack}</option>
        {/each}
    </select>
    {/if}
    <select class="select col-span-1" bind:value={$editor.language}>
        <option disabled selected value>Language</option>
        {#each languages as lang}
        <option value={lang}>{lang}</option>
        {/each}
    </select>
    <button class="btn variant-filled" on:click={parent.onClose}>× Close</button>
</div>
<div class="basis-full h-max ">
    <CodeMirror
        bind:value={$editor.function}
        lang={languages_func.get($editor.language)}
        theme={oneDark}
        class="max-h-[90vh] overflow-y-auto"
        styles={{
            "&": {
                maxWidth: "100%",
                height: "85vh",
            },
        }}
        />
</div>
