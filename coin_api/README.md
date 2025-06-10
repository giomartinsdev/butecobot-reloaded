# Coin API

Handles daily coin claims for the Chorume Bot ecosystem.

## Features
- Daily coin claim and claim history
- REST API for Discord bot integration

## Usage

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the service:
   ```sh
   uvicorn api_service:app --host 0.0.0.0 --port 5012 --reload
   ```

## Docker Compose
This service is included in the main `docker-compose.yml` and starts automatically with the full stack.

## Endpoints
- `POST /daily-coins` - Claim daily coins
- `GET /daily-coins/status/{client_id}` - Check claim status
- `GET /daily-coins/history/{client_id}` - Get claim history
- `GET /health` - Health check

---

See the main `DISCORD_BOT_GUIDE.md` for full integration details.
