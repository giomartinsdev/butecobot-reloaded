# GenAI API (C# Version)

This is a C# reimplementation of the Python GenAI API service, providing a consistent interface to multiple LLM providers.

## Features

- Unified API for different LLM providers (OpenAI, Gemini)
- Handles provider-specific quirks and limitations transparently
- Comprehensive logging for debugging and monitoring
- Error handling with appropriate HTTP status codes
- Docker support for easy deployment
- Integration with Discord bot

## Supported Providers

- OpenAI (GPT models)
- Gemini (Google's generative AI models)

## API Endpoints

### Generate Text
```
POST /GenAI/generate
```

Request Body:
```json
{
  "prompt": "Your prompt here",
  "provider": "openai", // optional, defaults to GENAI_DEFAULT_PROVIDER env variable or "openai"
  "systemPrompt": "Optional system instructions", // optional
  "model": "gpt-3.5-turbo" // optional, defaults to provider-specific default
}
```

Response:
```json
{
  "text": "Generated text response from the model",
  "provider": "The provider that was used",
  "model": "The model that was used"
}
```

### Health Check
```
GET /GenAI/health
```

Response:
```
Healthy
```

## Configuration

Configuration is handled through appsettings.json and environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GENAI_DEFAULT_PROVIDER`: Default LLM provider (default: "openai")

## Provider-Specific Details

### OpenAI
- Uses the Azure.AI.OpenAI client library
- Default model: gpt-3.5-turbo
- Supports system prompts natively

### Gemini
- Uses direct HTTP calls to the Gemini REST API
- Default model: gemini-1.5-flash
- **System Prompt Handling**: Gemini doesn't support the "system" role in API calls. When a system prompt is provided, it's combined with the user prompt as plain text with newlines:
  ```
  {systemPrompt}

  {userPrompt}
  ```
- Does not include any "role" field in the API payload to avoid the "Content with system role is not supported" error

## Error Handling

The API includes error handling for:
- Missing API keys
- Unsupported providers
- Provider-specific error responses
- Response parsing failures

All errors are logged and returned with appropriate HTTP status codes.

## Development

### Prerequisites
- .NET 9.0 SDK or later

### Running locally
```bash
cd ai_api
dotnet run
```

### Building the Docker image
```bash
docker build -t butecobot-reloaded/ai-api -f ai_api/Dockerfile .
```

### Running with Docker
```bash
docker run -p 5015:80 \
  -e OPENAI_API_KEY=your-key-here \
  -e GEMINI_API_KEY=your-key-here \
  butecobot-reloaded/ai-api
```

### Running with Docker Compose
From the root directory of the project:
```bash
docker-compose build ai-api
docker-compose up -d ai-api
```

The API will be accessible at http://localhost:5015 when using Docker Compose (mapped to port 80 inside the container).

### Testing
There are several ways to test the API:

1. **VS Code REST Client**: Use the provided ai_api.http file to test endpoints with the VS Code REST Client extension.

2. **Test Scripts**: Several test scripts are provided:
   ```bash
   # Basic API tests (for local development on port 5000)
   ./test_api.sh
   
   # Docker deployment tests (for Docker deployment on port 5015)
   ./test_docker.sh
   
   # Integration tests with Discord bot
   ./test_integration.sh
   ```

3. **cURL Commands**:
   ```bash
   # Health check
   curl http://localhost:5015/GenAI/health
   
   # Generate text with OpenAI
   curl -X POST http://localhost:5015/GenAI/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Tell me a joke", "provider": "openai"}'
   
   # Generate text with Gemini
   curl -X POST http://localhost:5015/GenAI/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Tell me a joke", "provider": "gemini"}'
   ```

## Deployment

For detailed deployment instructions, see the [Deployment Guide](DEPLOYMENT.md).
