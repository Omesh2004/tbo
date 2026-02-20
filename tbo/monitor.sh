#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Travel Data Pipeline - Service Monitor ===${NC}\n"

# Check if docker-compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}Services are not running. Starting...${NC}"
    docker-compose up -d
    sleep 5
fi

echo -e "${YELLOW}Service Status:${NC}"
docker-compose ps

echo -e "\n${YELLOW}Redis Stream Info:${NC}"
docker-compose exec -T redis redis-cli XINFO STREAM travel_data_stream 2>/dev/null || echo "Stream not yet created"

echo -e "\n${YELLOW}Kafka Topics:${NC}"
docker-compose exec -T kafka kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null || echo "Kafka not ready"

echo -e "\n${YELLOW}Latest Entries in Redis Stream:${NC}"
docker-compose exec -T redis redis-cli XRANGE travel_data_stream - + 2>/dev/null || echo "No data yet"

echo -e "\n${YELLOW}Travel Pipeline Logs (last 50 lines):${NC}"
docker-compose logs --tail=50 travel-pipeline

echo -e "\n${GREEN}✅ Monitor Complete${NC}"
