#!/bin/bash

# Chorume Bot Ecosystem - Setup Script
# This script helps you set up the environment and start the containers

echo "🤖 Chorume Bot Ecosystem Setup"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit the .env file with your actual API keys and Discord token"
    echo "   Required: DISCORD_TOKEN"
    echo "   Optional: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
    echo ""
    read -p "Press Enter after you've configured the .env file..."
fi

# Validate Discord token
if ! grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env; then
    echo "✅ Discord token appears to be configured"
else
    echo "⚠️  Warning: Discord token still has default value"
    echo "   Please update DISCORD_TOKEN in .env file"
fi

echo ""
echo "🚀 Starting Chorume Bot Ecosystem..."
echo "This will build and start all containers:"
echo "  - Bet API (port 5001)"
echo "  - Economy API (port 5002)"
echo "  - AI API (port 5003)"
echo "  - Discord Bot"
echo ""

# Build and start containers
docker-compose up --build -d

# Wait a moment for containers to start
echo "⏳ Waiting for containers to start..."
sleep 10

# Check container status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🔍 Health Checks:"

# Check API health endpoints
check_health() {
    local service=$1
    local port=$2
    local url="http://localhost:$port/health"
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is not responding"
    fi
}

check_health "Economy API" 5001

echo ""
echo "📋 Next Steps:"
echo "1. Invite your Discord bot to a server"
echo "2. Test bot commands like !help_chorume"
echo "3. Check logs with: docker-compose logs [service-name]"
echo "4. Stop with: docker-compose down"
echo ""
echo "🎉 Setup complete! Your Chorume Bot Ecosystem is running!"

