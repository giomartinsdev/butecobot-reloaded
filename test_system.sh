#!/bin/bash

echo "🧪 Chorume Bot Ecosystem - System Test"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test functions
test_api() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (Status: $response)${NC}"
        return 1
    fi
}

test_api_with_response() {
    local name=$1
    local url=$2
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url" 2>/dev/null)
    
    if [ -n "$response" ] && echo "$response" | grep -q "status"; then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "  Response: $response"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "  Response: $response"
        return 1
    fi
}

echo "🔍 Checking if services are running..."
docker-compose ps

echo ""
echo "🌐 Testing API Health Endpoints..."

# Test all health endpoints
test_api_with_response "Client API Health" "http://localhost:5000/health"
test_api_with_response "Balance API Health" "http://localhost:5001/health"
test_api_with_response "Coin API Health" "http://localhost:5002/health"

echo ""
echo "📊 Testing Database Connection..."

# Test if database is accessible
if docker-compose exec -T postgres-db pg_isready -U economyuser -d economydb >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
fi

echo ""
echo "🔧 Testing API Endpoints..."

# Test client API endpoints
echo "Testing Client API..."
test_api "GET /client/" "http://localhost:5000/client/"

# Create a test user
echo "Creating test user..."
curl -s -X POST "http://localhost:5000/client/" \
  -H "Content-Type: application/json" \
  -d '{"discordId": "123456789012345678", "name": "TestUser"}' > /dev/null

test_api "GET test user" "http://localhost:5000/client/discordId/123456789012345678"

# Test balance API
echo ""
echo "Testing Balance API..."
# Get the test user to use their ID
USER_RESPONSE=$(curl -s "http://localhost:5000/client/discordId/123456789012345678")
USER_ID=$(echo "$USER_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -n "$USER_ID" ]; then
    test_api "GET balance" "http://localhost:5001/balance/$USER_ID"
    
    # Add some balance
    curl -s -X POST "http://localhost:5001/balance/add" \
      -H "Content-Type: application/json" \
      -d "{\"clientId\": \"$USER_ID\", \"amount\": 100, \"description\": \"Test balance\"}" > /dev/null
    
    test_api "GET balance after add" "http://localhost:5001/balance/$USER_ID"
else
    echo -e "${YELLOW}⚠️  Skipping balance tests - no user ID found${NC}"
fi

# Test coin API
echo ""
echo "Testing Coin API..."
if [ -n "$USER_ID" ]; then
    # Test daily coins
    echo "Testing daily coin claim..."
    CLAIM_RESPONSE=$(curl -s -X POST "http://localhost:5002/daily-coins" \
      -H "Content-Type: application/json" \
      -d "{\"clientId\": \"$USER_ID\"}")
    
    if echo "$CLAIM_RESPONSE" | grep -q "claimed successfully"; then
        echo -e "${GREEN}✅ Daily coin claim successful${NC}"
    else
        echo -e "${YELLOW}⚠️  Daily coin claim response: $CLAIM_RESPONSE${NC}"
    fi
    
    test_api "GET claim history" "http://localhost:5002/daily-coins/history/$USER_ID"
else
    echo -e "${YELLOW}⚠️  Skipping coin tests - no user ID found${NC}"
fi

echo ""
echo "🤖 Checking Discord Bot Status..."

# Check if bot container is running
if docker-compose ps | grep -q "chorume_bot_container.*Up"; then
    echo -e "${GREEN}✅ Discord bot container is running${NC}"
    
    # Check bot logs for any startup errors
    BOT_LOGS=$(docker-compose logs --tail=20 chorume-bot 2>/dev/null)
    
    if echo "$BOT_LOGS" | grep -q "Logged in as"; then
        echo -e "${GREEN}✅ Discord bot logged in successfully${NC}"
    elif echo "$BOT_LOGS" | grep -q "DISCORD_TOKEN not found"; then
        echo -e "${YELLOW}⚠️  Discord bot missing token - please configure .env${NC}"
    elif echo "$BOT_LOGS" | grep -q "Incorrect login credentials"; then
        echo -e "${RED}❌ Discord bot has invalid token${NC}"
    else
        echo -e "${YELLOW}⚠️  Discord bot status unclear - check logs${NC}"
        echo "Recent logs:"
        echo "$BOT_LOGS" | tail -5
    fi
else
    echo -e "${RED}❌ Discord bot container is not running${NC}"
fi

echo ""
echo "📋 System Summary"
echo "=================="

# Count running services
RUNNING_SERVICES=$(docker-compose ps | grep "Up" | wc -l)
TOTAL_SERVICES=5

echo "Running Services: $RUNNING_SERVICES/$TOTAL_SERVICES"

if [ "$RUNNING_SERVICES" -eq "$TOTAL_SERVICES" ]; then
    echo -e "${GREEN}🎉 All services are running!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may not be running properly${NC}"
fi

echo ""
echo "🔗 Access URLs:"
echo "  Client API:  http://localhost:5000"
echo "  Balance API: http://localhost:5001" 
echo "  Coin API:    http://localhost:5002"
echo "  Database:    localhost:5432"

echo ""
echo "📝 Next Steps:"
echo "1. Configure Discord bot token in .env file"
echo "2. Invite bot to Discord server"
echo "3. Test slash commands like /register, /daily, /balance"

echo ""
echo "🛠️  Useful Commands:"
echo "  docker-compose logs chorume-bot    # View bot logs"
echo "  docker-compose logs [service]      # View service logs"
echo "  docker-compose restart [service]   # Restart a service"
echo "  docker-compose down                # Stop all services"
