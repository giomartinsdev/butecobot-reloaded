# Discord Bot Integration Guide

## Overview

The Chorume Bot has been fully implemented with Discord slash commands that integrate with all microservices in the ecosystem. The bot provides a complete economy system with user management, daily rewards, transfers, and leaderboards.

## 🎮 Available Slash Commands

### User Management
- `/register` - Register yourself in the economy system
- `/balance [user]` - Check your or another user's balance

### Economy Features  
- `/daily` - Claim your daily coins (once per day, 100 coins)
- `/transfer <user> <amount> [description]` - Transfer coins to another user

### Information & Stats
- `/leaderboard [limit]` - Show top users by balance (max 20)
- `/history [limit]` - View your transaction history (max 50)
- `/daily_history [limit]` - View your daily claim history (max 30)

### System
- `/status` - Check the health status of all microservices
- `/help` - Show all available commands

## 🚀 Quick Start

1. **Setup the environment:**
   ```bash
   ./start.sh
   ```

2. **Configure your Discord bot:**
   - Get your bot token from [Discord Developer Portal](https://discord.com/developers/applications)
   - Update the `DISCORD_TOKEN` in your `.env` file
   - Invite the bot to your server with proper permissions

3. **Start using the bot:**
   ```
   /register    # Register in the system
   /daily       # Claim your first coins
   /balance     # Check your balance
   ```

## 🏗️ Architecture

The Discord bot integrates with three main microservices:

```
Discord Bot (Python)
├── Client API (Port 5000) - User management
├── Balance API (Port 5001) - Economy operations  
├── Coin API (Port 5002) - Daily claims
└── PostgreSQL Database
```

### API Integration

The bot communicates with microservices through HTTP REST APIs:

- **Client API**: User registration, lookup, management
- **Balance API**: Balance checks, transfers, transaction history
- **Coin API**: Daily coin claims, claim history

## 🔧 Technical Details

### Bot Features
- **Slash Commands**: Modern Discord slash command interface
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Auto-Registration**: Automatically creates users when needed
- **Rich Embeds**: Beautiful Discord embeds with proper formatting
- **Input Validation**: Validates all user inputs and amounts
- **Service Health**: Monitors and reports microservice status

### Security Features
- **Balance Validation**: Checks sufficient funds before transfers
- **User Validation**: Ensures users exist before operations
- **Daily Limits**: One daily claim per user per day
- **Transfer Limits**: Prevents self-transfers and negative amounts

### Code Quality
- **Async/Await**: Full asynchronous programming for performance
- **Type Hints**: Complete type annotations for better code quality
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Recovery**: Graceful handling of service failures

## 📊 Microservice Endpoints

### Client API (Port 5000)
```
POST /client/                     # Create user
GET  /client/                     # Get all users  
GET  /client/{id}                 # Get user by ID
GET  /client/discordId/{discord_id} # Get user by Discord ID
PUT  /client/{id}                 # Update user
DELETE /client/{id}               # Delete user
GET  /health                      # Health check
```

### Balance API (Port 5001)
```
POST /balance/add                 # Add balance
POST /balance/subtract            # Subtract balance
POST /balance/transaction         # Transfer between users
GET  /balance/{user_id}           # Get user balance
GET  /balance/operations/{user_id} # Get transaction history
GET  /health                      # Health check
```

### Coin API (Port 5002)
```
POST /daily-coins                 # Claim daily coins
GET  /daily-coins/status/{client_id} # Check claim status
GET  /daily-coins/history/{client_id} # Get claim history
GET  /health                      # Health check
```

## 🛠️ Development

### Adding New Commands

To add a new slash command:

1. Create the command function with `@bot.tree.command()`
2. Add proper error handling and validation
3. Use `await interaction.response.defer()` for long operations
4. Create rich embeds for responses
5. Update the help command

Example:
```python
@bot.tree.command(name="new_command", description="Description here")
async def new_command(interaction: discord.Interaction):
    await interaction.response.defer()
    
    # Your logic here
    
    embed = discord.Embed(title="Result", color=discord.Color.green())
    await interaction.followup.send(embed=embed)
```

### Testing

Test individual microservices:
```bash
# Test APIs directly
curl http://localhost:5000/health  # Client API
curl http://localhost:5001/health  # Balance API  
curl http://localhost:5002/health  # Coin API

# View logs
docker-compose logs chorume-bot
docker-compose logs balance-api
```

## 🎨 Discord Bot Permissions

Required permissions for the bot:
- `Send Messages` - Send responses to commands
- `Use Slash Commands` - Register and use slash commands
- `Embed Links` - Send rich embeds
- `Read Message History` - Access to interaction context
- `View Channels` - See channels to respond in

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding to slash commands:**
   - Check bot permissions in the server
   - Verify bot token in `.env` file
   - Check if commands are synced with `docker-compose logs chorume-bot`

2. **API connection errors:**
   - Verify all services are running: `docker-compose ps`
   - Check service health: `curl http://localhost:5000/health`
   - Review service logs: `docker-compose logs [service-name]`

3. **Database connection issues:**
   - Ensure PostgreSQL is running
   - Check if migrations ran successfully
   - Verify database environment variables

### Debug Commands

```bash
# View all container status
docker-compose ps

# Check specific service logs
docker-compose logs -f chorume-bot
docker-compose logs -f balance-api

# Restart specific service
docker-compose restart chorume-bot

# Full system restart
docker-compose down && docker-compose up -d
```

## 🔮 Future Enhancements

Potential features to add:
- **Betting System**: Integration with sports betting
- **Mini-games**: Coin-based games and challenges
- **Admin Commands**: Administrative controls and moderation
- **Statistics**: Advanced user and server statistics
- **Scheduled Events**: Automatic events and rewards
- **Economy Tweaks**: Interest, taxes, or inflation mechanics

## 📝 Notes

- Daily claims reset at midnight UTC
- All amounts are stored as integers (no decimal coins)
- Transaction history is preserved indefinitely
- The bot automatically creates users when they first interact
- All monetary values are formatted with thousand separators for readability

---

Built with ❤️ using Discord.py, FastAPI, and PostgreSQL
