# Adding a New Microservice to Chorume Bot Ecosystem

This guide will walk you through the steps of implementing a new microservice for the Chorume Bot ecosystem. The system follows a microservice architecture where each service is independently deployable and can be written in any programming language.

## Table of Contents

1. [Overview of the Architecture](#overview-of-the-architecture)
2. [Step 1: Setting Up Your Microservice](#step-1-setting-up-your-microservice)
3. [Step 2: Implementing the API](#step-2-implementing-the-api)
4. [Step 3: Database Integration](#step-3-database-integration)
5. [Step 4: Adding to Docker Compose](#step-4-adding-to-docker-compose)
6. [Step 5: Integration with the Discord Bot](#step-5-integration-with-the-discord-bot)
7. [Step 6: Testing and Validation](#step-6-testing-and-validation)
8. [Example Implementation](#example-implementation)

## Overview of the Architecture

The Chorume Bot ecosystem consists of several microservices that communicate with each other:

- **Client API**: Manages user information
- **Balance API**: Handles user balances and transactions
- **Coin API**: Manages daily coin claims
- **Bet API**: Handles betting events and user bets
- **GenAI API**: Provides AI assistant functionality
- **Bot Service**: Discord bot that interacts with users
- **DB Migration Service**: Handles database schema migrations

Each service has its own Docker container and communicates over a shared Docker network.

## Step 1: Setting Up Your Microservice

1. Create a new directory for your microservice in the project root:

   ```bash
   mkdir my_new_service
   cd my_new_service
   ```

2. Create the basic file structure:

   ```
   my_new_service/
   ├── api_service.py (or main file in your language)
   ├── Dockerfile
   ├── README.md
   ├── requirements.txt (or equivalent for your language)
   └── models/
       └── (your model files)
   ```


3. Create a README.md documenting your service:

   ```md
   # My New Service

   Description of what this service does for the Chorume Bot ecosystem.

   ## Features
   - List key features
   - ...

   ## Usage
   1. Install dependencies
   2. Run the service

   ## Docker Compose
   This service is included in the main `docker-compose.yml`

   ## Endpoints
   - `GET /health` - Health check
   - `POST /your-endpoint` - Description
   - ...
   ```

## Step 2: Implementing the API

Regardless of the programming language you choose, your service should follow these principles:

1. **Health Endpoint**: Always implement a `/health` endpoint that returns a status message:

   ```cs
    // example in dotnet
    var builder = WebApplication.CreateBuilder(args);
    var app = builder.Build();

    app.MapGet("/health", () => Results.Ok(new { status = "healthy", service = "my-service" }));

    ```

2. **Error Handling**: Implement proper error handling and return appropriate HTTP status codes.

3. **Logging**: Set up logging to help with debugging.

### Node.js Example (Express)

```javascript
const express = require('express');
const app = express();
const port = process.env.PORT || 5000;
require('dotenv').config();

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'my-service' });
});

// Your endpoint
app.post('/your-endpoint', (req, res) => {
  try {
    // Your implementation here
    console.log('Processing request');
    res.json({ message: 'Success', data: {} });
  } catch (error) {
    console.error(`Error processing request: ${error}`);
    res.status(500).json({ detail: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Service listening at port ${port}`);
});
```

## Step 3: Database Integration

If your service needs database access:

1. Use the existing PostgreSQL database by connecting to it:

   ```python
   # Python example with SQLAlchemy
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   
   DATABASE_URL = os.getenv("DATABASE_URL")
   engine = create_engine(DATABASE_URL)
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

2. Create database entities in TypeScript for the migration service:

   ```typescript
   // Create a new file in db_migration_service/src/entity/YourEntity.ts
   import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from "typeorm";
   
   @Entity()
   export class YourEntity {
       @PrimaryGeneratedColumn()
       id!: number;
   
       @Column()
       name!: string;
   
       @Column()
       description!: string;
   
       @CreateDateColumn()
       createdAt!: Date;
   
       @UpdateDateColumn()
       updatedAt!: Date;
   }
   ```

3. Generate and run a migration:

   ```bash
   docker-compose run --rm db-migration-service npm run migration:generate -- src/migration/AddYourEntity
   ```

## Step 4: Adding to Docker Compose

Add your service to the `docker-compose.yml` file:

```yaml
services:
  # ... existing services ...

  my-new-service:
    build: ./my_new_service
    container_name: my_new_service_container
    ports:
      - "5015:5000"  # Choose an available port
    networks:
      - buteco_network
    depends_on:
      - postgres-db
      # Add other dependencies as needed
    env_file:
      - .env
    restart: unless-stopped
```

## Step 5: Integration with the Discord Bot
### This is not complex, is very simple. Just think this python function is the aggregator of the routes of the functions which will trigger your api

1. Add a URL constant in `buteco_bot/tools/constants.py`:

   ```python
   MYNEWSERVICE_API_URL = os.getenv('MYNEWSERVICE_API_URL', 'http://my-new-service:5000')
   ```

2. Create a new command file in `buteco_bot/commands/my_new_feature.py`:

   ```python
   import discord
   from discord import app_commands
   import aiohttp
   from tools.utils import make_api_request
   from tools.constants import MYNEWSERVICE_API_URL

   def my_new_feature_commands(bot):
       @bot.tree.command(name="my_command", description="Description of what your command does")
       @app_commands.describe(
           param1="Description of parameter 1",
           param2="Description of parameter 2"
       )
       async def my_command(interaction: discord.Interaction, param1: str, param2: int):
           """Docstring explaining what this command does."""
           await interaction.response.defer(ephemeral=True)
           
           async with aiohttp.ClientSession() as session:
               data = {
                   "param1": param1,
                   "param2": param2
               }
               
               status, response = await make_api_request(
                   session, 'POST', f"{MYNEWSERVICE_API_URL}/your-endpoint", data
               )
               
               if status == 200:
                   embed = discord.Embed(
                       title="✅ Success",
                       description="Your command was successful!",
                       color=discord.Color.green()
                   )
                   # Add more fields to the embed as needed
               else:
                   embed = discord.Embed(
                       title="❌ Error",
                       description="Something went wrong. Please try again.",
                       color=discord.Color.red()
                   )
           
           await interaction.followup.send(embed=embed, ephemeral=True)
   ```

3. Register your command module in `buteco_bot/bot.py`:

   ```python
   # Add import at the top
   from commands.my_new_feature import my_new_feature_commands

   # Add this line with the other command registrations
   my_new_feature_commands(bot)
   ```

4. Update the help command in `buteco_bot/commands/help.py` to include your new command:

   ```python
   # Add to the commands_info list in the help command function
   commands_info = [
       # ... existing commands ...
       ("", ""),
       ("🆕 **Your Command Category**", ""),
       ("/my_command", "Description of what your command does"),
   ]
   ```

5. Includes the api in the healthcheck `buteco_bot/tools/help_commands.health`:

   ```python
   # Add to the commands_info list in the help command function
    services = [
            # ... existing routes ...
            ("Your API", f"{YOURAPI}/health")
        ]
   ```

## Step 6: Testing and Validation

1. Rebuild and restart your containers:

   ```bash
   docker-compose up --build -d
   ```

2. Check the health of your service:

   ```bash
   curl http://localhost:5015/health
   ```

3. Test your Discord command manually through the Discord bot interface.

4. Check logs if something isn't working:

   ```bash
   docker-compose logs my-new-service
   docker-compose logs buteco-bot
   ```

## Example Implementation

Here's a simple example of implementing a "joke service" in `GO` that returns random jokes:

**Directory Structure:**
```
joke_api/
├── main.go
├── Dockerfile
├── go.mod
├── go.sum
└── models/
    └── joke_models.go
```

**main.go (addition):**
```go
    package main

    import (
        "log"
        "math/rand"
        "net/http"
        "time"

        "github.com/gin-gonic/gin"
        "github.com/joke_api_go/models"
    )

    var jokes = []models.Joke{
        {Text: "Why did the chicken cross the road? To get to the other side!"},
        {Text: "I told my wife she was drawing her eyebrows too high. She looked surprised."},
        {Text: "Why don't scientists trust atoms? Because they make up everything!"},
    }

    func init() {
        rand.NewSource(time.Now().UnixNano())
    }

    func main() {
        router := gin.Default()

        router.GET("/health", healthCheck)

        router.GET("/joke", getRandomJoke)

        port := ":5000"
        log.Printf("Joke API service listening on port %s", port)
        if err := router.Run(port); err != nil {
            log.Fatalf("Failed to run server: %v", err)
        }
    }

    func healthCheck(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "healthy", "service": "joke-api"})
    }

    func getRandomJoke(c *gin.Context) {
        randomIndex := rand.Intn(len(jokes))
        joke := jokes[randomIndex]
        c.JSON(http.StatusOK, models.JokeResponse{Joke: joke.Text, Category: joke.Category})
    }
```

**joke_models.go (addition):**
```go
    package models

    type Joke struct {
        Text     string `json:"text"`
        Category string `json:"category"`
    }

    type JokeResponse struct {
        Joke     string `json:"joke"`
    }
```

**go.mod (addition):**
```go
    module joke_api_go

    go 1.22

    require github.com/gin-gonic/gin v1.9.1

    require (
        github.com/bytedance/sonic v1.9.1
        github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311
        github.com/gabriel-vasile/mimetype v1.4.2
        github.com/gin-contrib/sse v0.1.0
        github.com/go-playground/locales v0.14.1
        github.com/go-playground/universal-translator v0.18.1
        github.com/go-playground/validator/v10 v10.14.0
        github.com/goccy/go-json v0.10.2
        github.com/json-iterator/go v1.1.12
        github.com/klauspost/cpuid/v2 v2.2.4
        github.com/leodido/go-urn v1.2.4
        github.com/mattn/go-isatty v0.0.19
        github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd
        github.com/modern-go/reflect2 v1.0.2
        github.com/pelletier/go-toml/v2 v2.0.8
        github.com/twitchyliquid64/golang-asm v0.15.1
        github.com/ugorji/go/codec v1.2.11
        golang.org/x/arch v0.3.0
        golang.org/x/crypto v0.9.0
        golang.org/x/net v0.10.0
        golang.org/x/sys v0.8.0
        golang.org/x/text v0.9.0
        google.golang.org/protobuf v1.30.0
        gopkg.in/yaml.v3 v3.0.1
)

```

**go.mod (addition):**
```dockerfile
    FROM golang:1.22-alpine AS builder

    WORKDIR /app

    COPY go.mod .
    COPY go.sum .

    RUN go mod download

    COPY . .

    RUN CGO_ENABLED=0 GOOS=linux go build -o /joke_api .

    FROM alpine:latest

    WORKDIR /app

    COPY --from=builder /joke_api .

    EXPOSE 5000

    CMD ["/joke_api"]
```

**docker-compose.yml (addition):**
```yaml
services:
  # ... existing services ...

  joke-api:
    build: ./joke_api
    container_name: joke_api_container
    ports:
      - "5015:5000"
    networks:
      - buteco_network
    env_file:
      - .env
    restart: unless-stopped
```

**Update buteco_bot/tools/constants.py:**
```python
    # Add this line
    JOKE_API_URL = os.getenv('JOKE_API_URL', 'http://joke-api:5000')
```

**Update buteco_bot/bot.py:**
```python
    # Add import
    from commands.joke import joke_commands

    # Add registration
    joke_commands(bot)
```

---

This documentation should give you a complete guide for implementing and integrating a new microservice into the Chorume Bot ecosystem. Remember to follow the project's coding standards and error handling practices to maintain consistency across services.

### The Importance of Dockerfile in Your Microservice

The Dockerfile is a critical component of your microservice for several reasons:

1. **Consistent Environments**: Ensures your service runs identically in development and production
2. **Dependency Management**: Explicitly defines all dependencies needed by your service
3. **Isolation**: Keeps your service and its dependencies separate from other microservices
4. **Scalability**: Makes it easy to scale your service horizontally when needed
5. **Portability**: Allows your service to run on any system that supports Docker
6. **Integration**: Enables seamless integration with the existing Chorume Bot ecosystem

A well-crafted Dockerfile should:
- Use an appropriate base image for your language
- Install only necessary dependencies
- Follow security best practices
- Be optimized for build speed and image size
- Expose the correct port for your service
- Set appropriate environment variables
- Define a clear entrypoint or CMD

## Dockerfile Best Practices for Your Microservice

Creating an effective Dockerfile is essential for the reliability and performance of your microservice in the Chorume Bot ecosystem. Below are examples of well-structured Dockerfiles for different programming languages:

### Python (FastAPI/Flask) Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "api_service:app", "--host", "0.0.0.0", "--port", "5000"]
```

### Node.js Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5000

CMD ["node", "index.js"]

### .NET Dockerfile

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /app

COPY *.csproj ./
RUN dotnet restore

COPY . ./
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:7.0
WORKDIR /app
COPY --from=build /app/out .

EXPOSE 5000

ENV ASPNETCORE_URLS=http://+:5000

ENTRYPOINT ["dotnet", "YourServiceName.dll"]
```

### Important Considerations for Your Dockerfile

1. **Base Image Selection**:
   - Use official, minimal images (alpine/slim variants when possible)
   - Consider security implications of your base image
   - Use specific version tags instead of `latest`

2. **Multi-stage Builds**:
   - Use multi-stage builds for compiled languages to reduce image size
   - Keep only runtime dependencies in the final image

3. **Layer Caching**:
   - Order your Dockerfile commands to maximize cache utilization
   - Install dependencies before copying application code
   - Group related RUN commands to reduce layers

4. **Security**:
   - Don't run containers as root when possible
   - Avoid installing unnecessary packages
   - Remove build tools in the final image
   - Don't include secrets in your Docker image

5. **Environment Variables**:
   - Use environment variables for configuration
   - Define default values for required variables

6. **Health Checks**:
   - Implement Docker health checks for better orchestration
   - Example: `HEALTHCHECK CMD curl -f http://localhost:5000/health || exit 1`

Following these best practices ensures your microservice will integrate smoothly with the Chorume Bot ecosystem while maintaining security, performance, and reliability.
