#!/bin/bash

# Chorume Bot Ecosystem - Unified Startup Script
# This script sets up the environment, builds, and starts all containers for the system

set -e

WORKDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$WORKDIR"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# .env setup
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit the .env file with your actual API keys and Discord token"
    echo "   Required: DISCORD_TOKEN"
    echo "   Optional: OPENAI_API_KEY, GEMINI_API_KEY, GENAI_DEFAULT_PROVIDER"
    echo "   Optional: DB_USER, DB_PASSWORD, DB_NAME, etc."
    echo ""
    read -p "Press Enter after you've configured the .env file..."
fi

if grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env; then
    echo "⚠️  Warning: Discord token still has default value"
    echo "   Please update DISCORD_TOKEN in .env file"
else
    echo "✅ Discord token appears to be configured"
fi

echo ""
echo "🚀 Starting Chorume Bot Ecosystem..."
echo "This will build and start all containers:"
echo "  - Client API (port 5000)"
echo "  - Balance API (port 5001)"
echo "  - Coin API (port 5002)"
echo "  - Bet API (port 5003)"
echo "  - GenAI API (port 5004)"
echo "  - Discord Bot"
echo "  - PostgreSQL Database"
echo ""

docker-compose up --build -d

echo "⏳ Waiting for containers to start..."
sleep 10

echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🔍 Health Checks:"

check_health() {
    local name=$1
    local url=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is not responding ($url)"
    fi
}

check_health "Client API" "http://localhost:5000/health"
check_health "Balance API" "http://localhost:5001/health"
check_health "Coin API" "http://localhost:5002/health"
check_health "Bet API" "http://localhost:5003/health"
check_health "GenAI API" "http://localhost:5004/health"

# Discord bot health is via logs
BOT_LOGS=$(docker-compose logs --tail=20 chorume-bot 2>/dev/null)
if echo "$BOT_LOGS" | grep -q "Logged in as"; then
    echo "✅ Discord bot logged in successfully"
else
    echo "⚠️  Discord bot status unclear - check logs with: docker-compose logs chorume-bot"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Invite your Discord bot to a server (see README.md)"
echo "2. Test bot commands like /help, /ai, /register, /balance, etc."
echo "3. Check logs with: docker-compose logs [service-name]"
echo "4. Stop with: docker-compose down"
echo ""
echo "🎉 Setup complete! Your Chorume Bot Ecosystem is running!"

