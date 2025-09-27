import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react'
import proxyOptions from './proxyOptions';
import tailwindcss from '@tailwindcss/vite';
import frappeReactUIPlugin from 'frappe-react-ui/vite'

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		react(),
		tailwindcss(),
		frappeReactUIPlugin( {
				transformHtml: false
			} ),
	],
	server: {
		port: 8080,
		host: '0.0.0.0',
		proxy: proxyOptions
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src')
		}
	},
	build: {
		outDir: '../hms/public/frontend',
		emptyOutDir: true,
		target: 'es2015',
		minify: 'terser',
	},
	optimizeDeps: {
		include: ['frappe-react-ui']
	},
	publicDir: 'public'
});
