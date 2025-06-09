# GenAI API Service

A flexible microservice for handling AI prompt calls, supporting multiple LLM providers (OpenAI, Gemini, etc.) and business-specific prompt fine-tuning.

## Features
- Supports OpenAI (ChatGPT), Gemini, and easily extendable to other LLMs
- Passes user prompt, provider, and optional system prompt for business logic
- Simple REST API

## Usage

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set environment variables for API keys:
   - `OPENAI_API_KEY` for OpenAI
   - `GEMINI_API_KEY` for Gemini
   - `GENAI_DEFAULT_PROVIDER` (optional, default: openai)
3. Run the service:
   ```sh
   uvicorn api_service:app --host 0.0.0.0 --port 8005 --reload
   ```
4. Call the `/generate` endpoint with JSON:
   ```json
   {
     "prompt": "Your question here",
     "provider": "openai",
     "system_prompt": "(optional business/system prompt)",
     "model": "(optional model name)"
   }
   ```

## Docker Compose
This service is included in the main `docker-compose.yml` and starts automatically with the full stack.

## Discord Integration
Use the `/ai` command in Discord to interact with this service via the bot.

---

See the main `DISCORD_BOT_GUIDE.md` for full integration details.
