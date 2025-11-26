# Docker-based Svelte Components Build

This directory contains Svelte components that are compiled as Web Components for use in the Alpine.js frontend. The build process runs entirely in Docker - no local Node.js required.

## Quick Start

Build the components:
```bash
cd /home/user/workspace/AdventureLog/frontend_alpine
./build_svelte_components.sh
```

This will:
1. Build a Docker image with Node.js
2. Compile Svelte components as Web Components
3. Extract the built files to `templates/static/svelte/`

## Project Structure

```
svelte_components/
├── Dockerfile              # Docker build configuration
├── package.json           # Dependencies
├── vite.config.js         # Vite build config
└── src/
    ├── index.js           # Entry point
    ├── AdventureMap.svelte      # Map component
    └── AdventureCalendar.svelte # Calendar component
```

## Reusing Existing Components

The `vite.config.js` has an alias pointing to the main Svelte frontend:
```javascript
'$lib': path.resolve('../frontend/src/lib')
```

This means you can import any component from the main frontend:
```javascript
import LocationCard from '$lib/components/LocationCard.svelte';
```
