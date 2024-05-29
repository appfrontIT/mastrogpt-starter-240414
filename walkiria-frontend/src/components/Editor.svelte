<script lang="ts">
    import fullscreen_icon from '$lib/fullscreen.svg'
    import CodeMirror from "svelte-codemirror-editor";
    import { javascript } from "@codemirror/lang-javascript";
    import { oneDark } from "@codemirror/theme-one-dark";
    import {EditorView, keymap} from "@codemirror/view"
    import {defaultKeymap} from "@codemirror/commands"
    import { AppRail, AppRailTile, AppRailAnchor, AppBar } from '@skeletonlabs/skeleton';
    
    let view: EditorView;
    let currentTile: number = 0;
    let value = "";

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
    
    // let myView = new EditorView({
    //     doc: "hello",
    //     extensions: [keymap.of(defaultKeymap)],
    //     parent: document.body
    // })
</script>
<div class="grid grid-cols-12 gap-4 space-y-1" style="height: 5vh;">
    <select class="select col-span-2">
        <option disabled selected value>Package</option>
        <option value="1">Package 1</option>
        <option value="2">Package 2</option>
        <option value="3">Package 3</option>
        <option value="4">Package 4</option>
        <option value="5">Package 5</option>
    </select>
    <input class="input col-span-4" title="Input (text)" type="text" placeholder="action name" />
    <input class="input col-span-4" title="Input (text)" type="text" placeholder="description" />
    <select class="select col-span-2">
        <option disabled selected value>Language</option>
        <option value="1">Language 1</option>
        <option value="2">Language 2</option>
        <option value="3">Language 3</option>
        <option value="4">Language 4</option>
        <option value="5">Language 5</option>
    </select>
</div>
<div class="grid h-full w-full grid-rows-[1fr_auto] grid-cols-11" style="height: 80vh;">
    <CodeMirror
        bind:value
        lang={javascript()}
        theme={oneDark}
        class="col-span-10 max-h-[80vh] overflow-y-auto"
        />
        <div class="grid w-full grid-rows-10 space-y-2" style="height: 80vh;">
            <button class="btn"><img src={fullscreen_icon} alt="expand to fullscreen"></button>
            <button class="btn">Test</button>
            <button class="btn">Watch</button>
            <button class="btn">Verify</button>
            <button class="btn">Actions</button>
            <button class="btn row-start-10">Deploy</button>
        </div>
</div>
