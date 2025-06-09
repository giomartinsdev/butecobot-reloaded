# Client API

Handles user management for the Chorume Bot ecosystem.

## Features
- Register, update, and delete users
- Lookup by Discord ID or internal ID
- REST API for Discord bot and other services

## Usage

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the service:
   ```sh
   uvicorn api_service:app --host 0.0.0.0 --port 5000 --reload
   ```

## Docker Compose
This service is included in the main `docker-compose.yml` and starts automatically with the full stack.

## Endpoints
- `POST /client/` - Create user
- `GET /client/` - List users
- `GET /client/{id}` - Get user by ID
- `GET /client/discordId/{discord_id}` - Get user by Discord ID
- `PUT /client/{id}` - Update user
- `DELETE /client/{id}` - Delete user
- `GET /health` - Health check

---

See the main `DISCORD_BOT_GUIDE.md` for full integration details.
