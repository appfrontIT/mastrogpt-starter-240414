import { join } from 'path'
import type { Config } from 'tailwindcss'
import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';
import { skeleton } from '@skeletonlabs/tw-plugin'
import { walkiriaTheme } from './walkiria-theme'

export default {
	darkMode: 'selector',
	content: ['./src/**/*.{html,js,svelte,ts}', join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}')],
	theme: {
	},
	plugins: [
		forms,
		typography,
		skeleton({
			themes: { preset: [ "crimson" ] }
		}),
	],
} satisfies Config;
