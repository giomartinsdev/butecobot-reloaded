#!/bin/bash

# Database Reset Script for Betting System
# This script will reset the database and run fresh migrations

set -e

echo "🔄 Resetting Database for Betting System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all containers...${NC}"
docker-compose down

echo -e "${YELLOW}Removing database volume...${NC}"
docker volume rm butecobot-reloaded_economy_data 2>/dev/null || echo "Volume doesn't exist, skipping..."

echo -e "${YELLOW}Building containers...${NC}"
docker-compose build

echo -e "${YELLOW}Starting database and migration services...${NC}"
docker-compose up -d postgres-db

# Wait for database to be ready
echo -e "${BLUE}Waiting for database to be ready...${NC}"
sleep 10

# Check if database is ready
until docker-compose exec postgres-db pg_isready -U chorume_user -d chorume_db; do
  echo "Waiting for database..."
  sleep 2
done

echo -e "${GREEN}Database is ready!${NC}"

echo -e "${YELLOW}Running migrations...${NC}"
docker-compose up db-migration-service

echo -e "${YELLOW}Starting all services...${NC}"
docker-compose up -d

echo -e "${GREEN}✅ Database reset complete!${NC}"
echo ""
echo -e "${BLUE}Services starting up...${NC}"
echo "- Balance API: http://localhost:5001"
echo "- Client API: http://localhost:5000" 
echo "- Coin API: http://localhost:5002"
echo "- Bet API: http://localhost:5003"
echo ""
echo -e "${YELLOW}Wait a few seconds for all services to be ready, then test with:${NC}"
echo "./test_betting_system.sh"
