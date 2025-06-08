#!/bin/bash

echo "🤖 Setting up Chorume Bot Ecosystem..."
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file with your Discord bot token!"
    echo "   1. Go to https://discord.com/developers/applications"
    echo "   2. Create a new application and bot"
    echo "   3. Copy the bot token"
    echo "   4. Replace 'your_discord_bot_token_here' in .env with your actual token"
    echo ""
    echo "Press Enter after you've configured the .env file with your Discord token..."
    read
fi

# Validate Discord token
if grep -q "your_discord_bot_token_here" .env; then
    echo "❌ Warning: Discord token still has default value!"
    echo "   Please update DISCORD_TOKEN in .env file before continuing"
    echo "   Press Enter to continue anyway or Ctrl+C to stop..."
    read
fi

echo ""
echo "🚀 Building and starting all services..."
echo "This will start:"
echo "  - PostgreSQL Database"
echo "  - Client API (Users) - Port 5000"
echo "  - Balance API (Economy) - Port 5001" 
echo "  - Coin API (Daily Claims) - Port 5002"
echo "  - Discord Bot"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start
echo "🔨 Building containers..."
docker-compose build

echo "▶️  Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 15

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm db-migration-service npm run migration:run

echo ""
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "🔍 Testing API health..."

check_api() {
    local name=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is not responding"
    fi
}

sleep 5
check_api "Client API" "http://localhost:5000/health"
check_api "Balance API" "http://localhost:5001/health"
check_api "Coin API" "http://localhost:5002/health"

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Invite your Discord bot to a server with these permissions:"
echo "   - Send Messages"
echo "   - Use Slash Commands"
echo "   - Embed Links"
echo "   - Read Message History"
echo ""
echo "2. Test the bot with these slash commands:"
echo "   /help     - Show all commands"
echo "   /register - Register in the economy"
echo "   /daily    - Claim daily coins"
echo "   /balance  - Check your balance"
echo ""
echo "📝 Useful Commands:"
echo "   docker-compose logs chorume-bot    - View bot logs"
echo "   docker-compose logs [service]      - View service logs"
echo "   docker-compose down                - Stop all services"
echo "   docker-compose up -d               - Start all services"
echo ""
echo "🎮 Happy gaming!"
