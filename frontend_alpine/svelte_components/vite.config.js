import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
  plugins: [
    svelte({
      compilerOptions: {
        customElement: true // Compile as web components
      }
    })
  ],
  resolve: {
    alias: {
      '$lib': path.resolve('./src/lib')
    }
  },
  build: {
    lib: {
      entry: './src/index.js',
      name: 'AdventureLogComponents',
      fileName: 'components',
      formats: ['iife']
    },
    outDir: './dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        entryFileNames: 'components.js',
        assetFileNames: 'components.[ext]'
      }
    }
  }
});
