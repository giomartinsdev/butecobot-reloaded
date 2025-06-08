# Chorume Bot Ecosystem

A comprehensive Discord bot ecosystem built with Docker containers, featuring economy management, daily rewards, user transfers, and microservices architecture.

## 🎮 Discord Bot Features

The Chorume Bot provides a complete economy system through Discord slash commands:

### 💰 Economy Commands
- `/register` - Join the economy system
- `/daily` - Claim daily coins (100 coins/day)
- `/balance [user]` - Check coin balance
- `/transfer <user> <amount>` - Send coins to other users
- `/leaderboard` - View top users by balance
- `/history` - View transaction history

### 📊 Information Commands  
- `/status` - Check all microservices health
- `/help` - Show all available commands
- `/daily_history` - View daily claim history

## 🚀 Quick Start

1. **Setup the system:**
   ```bash
   ./start.sh
   ```

2. **Configure Discord bot:**
   - Get bot token from [Discord Developer Portal](https://discord.com/developers/applications)
   - Edit `.env` file with your `DISCORD_TOKEN`
   - Invite bot to your server with slash command permissions

3. **Start using:**
   ```
   /register    # Join the economy
   /daily       # Get your first coins
   /balance     # Check your wealth
   ```

## Architecture

The system uses a microservices architecture with Docker containers communicating through a shared network. Each container is independently deployable and scalable, making it easy to add new features or support additional programming languages.

```
┌─────────────────────┐
│  ChorumeBotContainer│
│  (Discord Bot)      │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │   Docker    │
    │   Network   │
    └──────┬──────┘
           │
┌──────────┼──────────┐
│          │          │
▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│  API1   │ │  API2   │ |   API2  │
│Container│ │Container│ |Container│
└─────────┘ └─────────┘ └─────────┘
```

## Features

### Economy System
- Virtual coin system with daily rewards
- Peer-to-peer coin transfers
- "Airplane" distribution system (inspired by Silvio Santos)
- Leaderboard and transaction history

### Discord Bot
- Comprehensive command system
- Rich embed responses
- Error handling and status monitoring
- User-friendly help system

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Discord Bot Token

### Setup

1. Clone or download the project files
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file with your credentials:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token to your `.env` file
4. Invite the bot to your server with appropriate permissions

## Container Details

### economyApiContainer

**Port**: 5002 (external) → 5000 (internal)

**Endpoints**:
- `POST /coin/get-daily` - Claim daily coins
- `GET /coin/show` - Show user balance
- `POST /coin/transfer` - Transfer coins between users
- `PUT /coin/update` - Update user balance (admin)
- `DELETE /coin/remove` - Remove user from system
- `POST /airplane/distribute` - Distribute coins among multiple users
- `GET /transactions` - Get transaction history
- `GET /leaderboard` - Get coin leaderboard
### ChorumeBotContainer

**Discord Commands**:

**Economy Commands**:
- `!balance` - Check your coin balance
- `!daily` - Claim daily coins (50-200 random amount)
- `!transfer @user amount` - Transfer coins to another user
- `!airplane amount @user1 @user2...` - Distribute coins randomly among users
- `!leaderboard` - Show top 10 users by coin balance

**Utility Commands**:
- `!help_chorume` - Show all available commands
- `!status` - Check system status

## Development

### Adding New Containers

The architecture is designed to be language-agnostic. To add a new container in a different language:

1. Create a new directory for your container
2. Implement the required API endpoints
3. Add the service to `docker-compose.yml`
4. Update the Discord bot to interact with the new service

### Example: Adding a Node.js Container

```yaml
# In docker-compose.yml
new-service:
  build: ./newServiceContainer
  container_name: new_service_container
  ports:
    - "5004:3000"
  networks:
    - chorume_network
```

### API Standards

All containers should implement:
- Health check endpoint (`/health`)
- CORS support for cross-origin requests
- JSON request/response format
- Proper error handling with HTTP status codes

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Discord bot token | Yes |

### Docker Compose Configuration

The `docker-compose.yml` file defines:
- Service dependencies
- Port mappings
- Environment variable passing
- Network configuration
- Restart policies

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check Discord token and bot permissions
2. **API containers not accessible**: Verify Docker network configuration
4. **Database persistence**: Current implementation uses in-memory storage

### Logs

View container logs:
```bash
docker-compose logs [service-name]
```

### Health Checks

Check service status:
```bash
curl http://localhost:5002/health  # Economy API
```

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions
- Implement proper error handling

### Testing

- Add unit tests for new features
- Test API endpoints with proper error cases
- Verify Discord bot commands work correctly

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review container logs
3. Verify environment configuration
4. Test individual API endpoints

---

*Built with ❤️ using Docker, Python, and Discord.py*
