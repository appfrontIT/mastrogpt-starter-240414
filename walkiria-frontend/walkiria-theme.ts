
import type { CustomThemeConfig } from '@skeletonlabs/tw-plugin';

export const walkiriaTheme: CustomThemeConfig = {
    name: 'walkiria-theme',
    properties: {
		// =~= Theme Properties =~=
		"--theme-font-family-base": `system-ui`,
		"--theme-font-family-heading": `system-ui`,
		"--theme-font-color-base": "0 0 0",
		"--theme-font-color-dark": "255 255 255",
		"--theme-rounded-base": "9999px",
		"--theme-rounded-container": "8px",
		"--theme-border-base": "1px",
		// =~= Theme On-X Colors =~=
		"--on-primary": "255 255 255",
		"--on-secondary": "0 0 0",
		"--on-tertiary": "255 255 255",
		"--on-success": "0 0 0",
		"--on-warning": "0 0 0",
		"--on-error": "255 255 255",
		"--on-surface": "255 255 255",
		// =~= Theme Colors  =~=
		// primary | #9c1fed 
		"--color-primary-50": "240 221 252", // #f0ddfc
		"--color-primary-100": "235 210 251", // #ebd2fb
		"--color-primary-200": "230 199 251", // #e6c7fb
		"--color-primary-300": "215 165 248", // #d7a5f8
		"--color-primary-400": "186 98 242", // #ba62f2
		"--color-primary-500": "156 31 237", // #9c1fed
		"--color-primary-600": "140 28 213", // #8c1cd5
		"--color-primary-700": "117 23 178", // #7517b2
		"--color-primary-800": "94 19 142", // #5e138e
		"--color-primary-900": "76 15 116", // #4c0f74
		// secondary | #12de98 
		"--color-secondary-50": "219 250 240", // #dbfaf0
		"--color-secondary-100": "208 248 234", // #d0f8ea
		"--color-secondary-200": "196 247 229", // #c4f7e5
		"--color-secondary-300": "160 242 214", // #a0f2d6
		"--color-secondary-400": "89 232 183", // #59e8b7
		"--color-secondary-500": "18 222 152", // #12de98
		"--color-secondary-600": "16 200 137", // #10c889
		"--color-secondary-700": "14 167 114", // #0ea772
		"--color-secondary-800": "11 133 91", // #0b855b
		"--color-secondary-900": "9 109 74", // #096d4a
		// tertiary | #8214c7 
		"--color-tertiary-50": "236 220 247", // #ecdcf7
		"--color-tertiary-100": "230 208 244", // #e6d0f4
		"--color-tertiary-200": "224 196 241", // #e0c4f1
		"--color-tertiary-300": "205 161 233", // #cda1e9
		"--color-tertiary-400": "168 91 216", // #a85bd8
		"--color-tertiary-500": "130 20 199", // #8214c7
		"--color-tertiary-600": "117 18 179", // #7512b3
		"--color-tertiary-700": "98 15 149", // #620f95
		"--color-tertiary-800": "78 12 119", // #4e0c77
		"--color-tertiary-900": "64 10 98", // #400a62
		// success | #07f0f1 
		"--color-success-50": "218 253 253", // #dafdfd
		"--color-success-100": "205 252 252", // #cdfcfc
		"--color-success-200": "193 251 252", // #c1fbfc
		"--color-success-300": "156 249 249", // #9cf9f9
		"--color-success-400": "81 245 245", // #51f5f5
		"--color-success-500": "7 240 241", // #07f0f1
		"--color-success-600": "6 216 217", // #06d8d9
		"--color-success-700": "5 180 181", // #05b4b5
		"--color-success-800": "4 144 145", // #049091
		"--color-success-900": "3 118 118", // #037676
		// warning | #ebd703 
		"--color-warning-50": "252 249 217", // #fcf9d9
		"--color-warning-100": "251 247 205", // #fbf7cd
		"--color-warning-200": "250 245 192", // #faf5c0
		"--color-warning-300": "247 239 154", // #f7ef9a
		"--color-warning-400": "241 227 79", // #f1e34f
		"--color-warning-500": "235 215 3", // #ebd703
		"--color-warning-600": "212 194 3", // #d4c203
		"--color-warning-700": "176 161 2", // #b0a102
		"--color-warning-800": "141 129 2", // #8d8102
		"--color-warning-900": "115 105 1", // #736901
		// error | #686642 
		"--color-error-50": "232 232 227", // #e8e8e3
		"--color-error-100": "225 224 217", // #e1e0d9
		"--color-error-200": "217 217 208", // #d9d9d0
		"--color-error-300": "195 194 179", // #c3c2b3
		"--color-error-400": "149 148 123", // #95947b
		"--color-error-500": "104 102 66", // #686642
		"--color-error-600": "94 92 59", // #5e5c3b
		"--color-error-700": "78 77 50", // #4e4d32
		"--color-error-800": "62 61 40", // #3e3d28
		"--color-error-900": "51 50 32", // #333220
		// surface | #9214b3 
		"--color-surface-50": "239 220 244", // #efdcf4
		"--color-surface-100": "233 208 240", // #e9d0f0
		"--color-surface-200": "228 196 236", // #e4c4ec
		"--color-surface-300": "211 161 225", // #d3a1e1
		"--color-surface-400": "179 91 202", // #b35bca
		"--color-surface-500": "146 20 179", // #9214b3
		"--color-surface-600": "131 18 161", // #8312a1
		"--color-surface-700": "110 15 134", // #6e0f86
		"--color-surface-800": "88 12 107", // #580c6b
		"--color-surface-900": "72 10 88", // #480a58
		
	}
}