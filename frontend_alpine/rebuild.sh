#!/bin/bash
set -e

echo "🔨 Building Svelte components..."
./build_svelte_components.sh

echo ""
echo "🌍 Building Alpine.js frontend..."
python3 build.py

echo ""
echo "🐳 Building and restarting Docker container..."
cd ..
docker compose -f docker-compose.test.yml build frontend-alpine
docker compose -f docker-compose.test.yml down frontend-alpine
docker compose -f docker-compose.test.yml up -d frontend-alpine

echo ""
echo "✅ Frontend rebuilt and restarted successfully!"
echo "📍 Access at: http://localhost:3000"
