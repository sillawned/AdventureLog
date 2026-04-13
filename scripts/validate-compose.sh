#!/bin/bash
# ============================================================================
# Docker Compose Validation Script
# ============================================================================
#
# This script validates all Docker Compose configuration files for syntax
# errors and common issues.
#
# Usage: ./scripts/validate-compose.sh
#
# ============================================================================

set -e

echo "🔍 Validating Docker Compose files..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for results
PASSED=0
FAILED=0

# Compose files to validate
COMPOSE_FILES=(
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker-compose-traefik.yaml"
)

# Validate each compose file
for compose_file in "${COMPOSE_FILES[@]}"; do
    if [ ! -f "$compose_file" ]; then
        echo -e "${YELLOW}⚠️  Skipping $compose_file (not found)${NC}"
        continue
    fi

    echo "Validating $compose_file..."

    if docker-compose -f "$compose_file" config > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $compose_file is valid${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ $compose_file has errors:${NC}"
        docker-compose -f "$compose_file" config
        FAILED=$((FAILED + 1))
    fi
    echo ""
done

# Summary
echo "============================================================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All compose files are valid! ($PASSED validated)${NC}"
    exit 0
else
    echo -e "${RED}✗ Validation failed: $FAILED file(s) with errors${NC}"
    exit 1
fi
