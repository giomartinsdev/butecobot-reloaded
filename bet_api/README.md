# Bet API

Handles all betting operations for the Buteco Bot ecosystem.

## Features
- Create, list, and manage betting events
- Place, finalize, and cancel bets
- REST API for Discord bot integration

## Usage

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the service:
   ```sh
   uvicorn api_service:app --host 0.0.0.0 --port 5013 --reload
   ```

## Docker Compose
This service is included in the main `docker-compose.yml` and starts automatically with the full stack.

## Endpoints
- `POST /bet/event` - Create event
- `GET /bet/events` - List events
- `POST /bet/place` - Place a bet
- `POST /bet/finalize` - Finalize event
- `POST /bet/cancel` - Cancel event
- `GET /health` - Health check

---

See the main `DISCORD_BOT_GUIDE.md` for full integration details.
