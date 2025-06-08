# Troubleshooting Guide - Chorume Bot Ecosystem

## 🚨 Common Issues and Solutions

### Discord Bot Issues

#### Bot not responding to commands
**Symptoms:** Bot is online but doesn't respond to slash commands
**Solutions:**
1. Check if slash commands are synced:
   ```bash
   docker-compose logs chorume-bot | grep -i "synced"
   ```
2. Verify bot permissions in Discord server:
   - Send Messages ✅
   - Use Slash Commands ✅
   - Embed Links ✅
   - Read Message History ✅
3. Check bot token configuration:
   ```bash
   grep DISCORD_TOKEN .env
   ```

#### Bot shows as offline
**Symptoms:** Bot appears offline in Discord
**Solutions:**
1. Check container status:
   ```bash
   docker-compose ps chorume-bot
   ```
2. View bot logs:
   ```bash
   docker-compose logs chorume-bot
   ```
3. Common error messages:
   - `DISCORD_TOKEN not found` → Configure token in .env
   - `Incorrect login credentials` → Invalid token
   - `Connection error` → Network/firewall issues

#### Slash commands return errors
**Symptoms:** Commands trigger but return error messages
**Solutions:**
1. Check API service health:
   ```bash
   curl http://localhost:5000/health  # Client API
   curl http://localhost:5001/health  # Balance API
   curl http://localhost:5002/health  # Coin API
   ```
2. Verify service connectivity:
   ```bash
   docker-compose logs chorume-bot | grep -i "api request failed"
   ```

### API Service Issues

#### Services not starting
**Symptoms:** `docker-compose ps` shows services as "Exit" or "Restarting"
**Solutions:**
1. Check individual service logs:
   ```bash
   docker-compose logs client-api
   docker-compose logs balance-api
   docker-compose logs coin-api
   ```
2. Common issues:
   - Database not ready → Wait for PostgreSQL to fully start
   - Missing environment variables → Check .env file
   - Port conflicts → Ensure ports 5000-5002 are available

#### Database connection errors
**Symptoms:** APIs failing with database connection errors
**Solutions:**
1. Check PostgreSQL status:
   ```bash
   docker-compose ps postgres-db
   docker-compose logs postgres-db
   ```
2. Verify database credentials:
   ```bash
   docker-compose exec postgres-db pg_isready -U economyuser -d economydb
   ```
3. Run migrations manually:
   ```bash
   docker-compose run --rm db-migration-service npm run migration:run
   ```

#### API returning 404/500 errors
**Symptoms:** API calls fail with HTTP error codes
**Solutions:**
1. Check specific API logs:
   ```bash
   docker-compose logs [service-name]
   ```
2. Test endpoints manually:
   ```bash
   curl -v http://localhost:5000/health
   ```
3. Verify database schema:
   ```bash
   docker-compose exec postgres-db psql -U economyuser -d economydb -c "\dt"
   ```

### Environment Issues

#### Missing .env file
**Symptoms:** Services fail to start with environment variable errors
**Solutions:**
1. Copy from template:
   ```bash
   cp .env.example .env
   ```
2. Configure required variables:
   ```bash
   nano .env  # or your preferred editor
   ```

#### Port conflicts
**Symptoms:** "Port already in use" errors
**Solutions:**
1. Check what's using the ports:
   ```bash
   lsof -i :5000
   lsof -i :5001
   lsof -i :5002
   lsof -i :5432
   ```
2. Stop conflicting services or change ports in docker-compose.yml

#### Permission errors
**Symptoms:** Docker permission denied errors
**Solutions:**
1. Add user to docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```
2. Or use sudo with docker commands:
   ```bash
   sudo docker-compose up -d
   ```

### Database Issues

#### PostgreSQL won't start
**Symptoms:** Database container exits immediately
**Solutions:**
1. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres-db
   ```
2. Clear data volume if corrupted:
   ```bash
   docker-compose down
   docker volume rm butecobot-reloaded_economy_data
   docker-compose up -d
   ```
3. Verify environment variables:
   ```bash
   grep DB_ .env
   ```

#### Migration failures
**Symptoms:** Migration service fails to run
**Solutions:**
1. Check migration logs:
   ```bash
   docker-compose logs db-migration-service
   ```
2. Run migrations manually:
   ```bash
   docker-compose run --rm db-migration-service npm run migration:run
   ```
3. Check database connectivity:
   ```bash
   docker-compose exec postgres-db psql -U economyuser -d economydb -c "SELECT version();"
   ```

## 🛠️ Diagnostic Commands

### System Health Check
```bash
# Run comprehensive system test
./test_system.sh

# Check all container status
docker-compose ps

# View all logs
docker-compose logs

# Check resource usage
docker stats
```

### Individual Service Debugging
```bash
# Bot debugging
docker-compose logs -f chorume-bot
docker-compose exec chorume-bot /bin/bash  # if container running

# API debugging
docker-compose logs -f client-api
docker-compose logs -f balance-api
docker-compose logs -f coin-api

# Database debugging
docker-compose logs -f postgres-db
docker-compose exec postgres-db psql -U economyuser -d economydb
```

### Network Debugging
```bash
# Test internal network connectivity
docker-compose exec chorume-bot ping client-api
docker-compose exec chorume-bot ping balance-api
docker-compose exec chorume-bot ping coin-api

# Test external API access
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

## 🔄 Recovery Procedures

### Complete System Reset
```bash
# Stop everything
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker volume prune

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Wait and run migrations
sleep 30
docker-compose run --rm db-migration-service npm run migration:run
```

### Restart Individual Services
```bash
# Restart just the bot
docker-compose restart chorume-bot

# Restart APIs
docker-compose restart client-api balance-api coin-api

# Restart database (be careful!)
docker-compose restart postgres-db
```

### Update and Redeploy
```bash
# Update code and redeploy
git pull  # if using git
docker-compose build
docker-compose up -d
```

## 📊 Monitoring

### Log Monitoring
```bash
# Real-time logs
docker-compose logs -f

# Filter logs by service
docker-compose logs -f chorume-bot | grep ERROR

# Log rotation (if logs get too large)
docker-compose logs --since="1h"
```

### Performance Monitoring
```bash
# Container resource usage
docker stats

# Disk usage
docker system df

# Network usage
docker network ls
```

## 🆘 Getting Help

### Information to Gather
When seeking help, provide:
1. Output of `docker-compose ps`
2. Relevant logs from `docker-compose logs [service]`
3. Your .env file (without sensitive tokens)
4. Error messages and symptoms
5. Steps to reproduce the issue

### Log Collection Script
```bash
#!/bin/bash
# Collect diagnostic information
echo "=== Container Status ===" > debug_info.txt
docker-compose ps >> debug_info.txt

echo -e "\n=== Bot Logs ===" >> debug_info.txt
docker-compose logs --tail=50 chorume-bot >> debug_info.txt

echo -e "\n=== API Logs ===" >> debug_info.txt
docker-compose logs --tail=20 client-api balance-api coin-api >> debug_info.txt

echo -e "\n=== Database Logs ===" >> debug_info.txt
docker-compose logs --tail=20 postgres-db >> debug_info.txt

echo "Debug info collected in debug_info.txt"
```

### Emergency Contacts
- Check project documentation
- Review GitHub issues (if applicable)
- Discord/community support channels
- System administrator

---

💡 **Pro Tip:** Keep this guide handy and run `./test_system.sh` regularly to catch issues early!
