import { purgeCss } from 'vite-plugin-tailwind-purgecss';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	assetsInclude: ["**/*.yaml"],
	plugins: [sveltekit(), purgeCss()],
	optimizeDeps: {
        exclude: ["svelte-codemirror-editor", "codemirror", "@codemirror/language-javascript" /* ... */],
    },
	server: {
		port: 8080,
		proxy: {
			"/api/my": {
				target: process.env.NUVDEV_HOST,
				changeOrigin: true
			}
		}
	}
});