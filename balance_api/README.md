# Balance API

Handles all balance and transaction operations for the Buteco Bot ecosystem.

## Features
- Add, subtract, and transfer coins between users
- Transaction history and balance queries
- REST API for integration with Discord bot and other services

## Usage

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the service:
   ```sh
   uvicorn api_service:app --host 0.0.0.0 --port 5011 --reload
   ```

## Docker Compose
This service is included in the main `docker-compose.yml` and starts automatically with the full stack.

## Endpoints
- `POST /balance/add` - Add balance
- `POST /balance/subtract` - Subtract balance
- `POST /balance/transaction` - Transfer between users
- `GET /balance/{user_id}` - Get user balance
- `GET /balance/operations/{user_id}` - Get transaction history
- `GET /health` - Health check

---

See the main `DISCORD_BOT_GUIDE.md` for full integration details.
