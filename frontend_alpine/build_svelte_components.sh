#!/bin/bash
set -e

echo "🔨 Building Svelte components..."

# Build the components using Docker (build stage only)
docker build --target builder -t adventurelog-svelte-builder ./svelte_components

# Create a container and extract files
echo "📦 Extracting built components..."
CONTAINER_ID=$(docker create adventurelog-svelte-builder)
docker cp "$CONTAINER_ID:/app/dist/." ./templates/static/svelte/
docker rm "$CONTAINER_ID"

echo "✅ Components built successfully in templates/static/svelte/"
echo "📦 Files:"
ls -lh ./templates/static/svelte/
