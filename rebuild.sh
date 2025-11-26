#!/bin/bash
set -e

echo "🌍 Building frontend..."
cd ./frontend_alpine
sh ./rebuild.sh

echo "🐳 Building and restarting Docker container..."
cd ..
docker compose -f docker-compose.test.yml build
docker compose -f docker-compose.test.yml down
docker compose -f docker-compose.test.yml up -d