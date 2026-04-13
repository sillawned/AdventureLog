#!/bin/bash
# ============================================================================
# AdventureLog Service Health Check Script
# ============================================================================
#
# This script verifies that all running services are healthy and responding.
#
# Usage:
#   ./scripts/health-check.sh              # Check current compose (docker-compose.yml)
#   ./scripts/health-check.sh dev          # Check dev compose (docker-compose.dev.yml)
#   ./scripts/health-check.sh traefik      # Check traefik compose (docker-compose-traefik.yaml)
#
# ============================================================================

# Determine which compose file to use
COMPOSE_TYPE="${1:-prod}"
case "$COMPOSE_TYPE" in
    dev)
        COMPOSE_FILE="docker-compose.dev.yml"
        ;;
    traefik)
        COMPOSE_FILE="docker-compose-traefik.yaml"
        ;;
    prod|*)
        COMPOSE_FILE="docker-compose.yml"
        ;;
esac

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 AdventureLog Service Health Check${NC}"
echo "Using: $COMPOSE_FILE"
echo ""

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}✗ Compose file not found: $COMPOSE_FILE${NC}"
    exit 1
fi

# Get list of services
SERVICES=$(docker-compose -f "$COMPOSE_FILE" config --services)

# Check if services are running
if [ -z "$SERVICES" ]; then
    echo -e "${RED}✗ No services found in $COMPOSE_FILE${NC}"
    exit 1
fi

echo "Services to check:"
echo "$SERVICES" | sed 's/^/  - /'
echo ""

# Health check results
HEALTHY=0
UNHEALTHY=0
NO_HEALTH_CHECK=0

# Check each service
for service in $SERVICES; do
    # Get container ID
    CONTAINER_ID=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)

    if [ -z "$CONTAINER_ID" ]; then
        echo -e "${YELLOW}⚠ $service: Not running${NC}"
        UNHEALTHY=$((UNHEALTHY + 1))
        continue
    fi

    # Check service status
    STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_ID" 2>/dev/null || echo "unknown")

    if [ "$STATUS" != "running" ]; then
        echo -e "${RED}✗ $service: $STATUS${NC}"
        UNHEALTHY=$((UNHEALTHY + 1))
        continue
    fi

    # Check health status (if healthcheck is defined)
    HEALTH=$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER_ID" 2>/dev/null || echo "none")

    case "$HEALTH" in
        "healthy")
            echo -e "${GREEN}✓ $service: Healthy${NC}"
            HEALTHY=$((HEALTHY + 1))
            ;;
        "unhealthy")
            echo -e "${RED}✗ $service: Unhealthy${NC}"
            UNHEALTHY=$((UNHEALTHY + 1))
            # Show health check logs
            echo "   Health check output:"
            docker inspect -f '{{range .State.Health.Log}}{{println .Output}}{{end}}' "$CONTAINER_ID" | tail -1 | sed 's/^/     /'
            ;;
        "starting")
            echo -e "${YELLOW}⏳ $service: Starting (health check pending)${NC}"
            NO_HEALTH_CHECK=$((NO_HEALTH_CHECK + 1))
            ;;
        "none")
            # Service is running but has no health check
            if [ "$STATUS" = "running" ]; then
                echo -e "${BLUE}ℹ $service: Running (no health check defined)${NC}"
                HEALTHY=$((HEALTHY + 1))
            fi
            ;;
        *)
            echo -e "${YELLOW}⚠ $service: Unknown health status ($HEALTH)${NC}"
            NO_HEALTH_CHECK=$((NO_HEALTH_CHECK + 1))
            ;;
    esac
done

# Print summary
echo ""
echo "============================================================================"
echo -e "${BLUE}📊 Summary:${NC}"
echo -e "  ${GREEN}Healthy: $HEALTHY${NC}"
if [ $NO_HEALTH_CHECK -gt 0 ]; then
    echo -e "  ${BLUE}Starting/No check: $NO_HEALTH_CHECK${NC}"
fi
if [ $UNHEALTHY -gt 0 ]; then
    echo -e "  ${RED}Unhealthy: $UNHEALTHY${NC}"
fi

# Exit with appropriate code
if [ $UNHEALTHY -eq 0 ]; then
    if [ $NO_HEALTH_CHECK -eq 0 ]; then
        echo -e "${GREEN}✓ All services are healthy!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ Some services are still starting. Check again in a few seconds.${NC}"
        exit 0
    fi
else
    echo -e "${RED}✗ Some services are unhealthy. Run 'docker-compose logs' for details.${NC}"
    exit 1
fi
