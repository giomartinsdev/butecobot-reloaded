# Database Service for Migrations

This service handles database connections and migrations using TypeScript and TypeORM.

## Features
- Runs database migrations
- Connects to PostgreSQL

## Usage
- Use Docker Compose to run the service
- Exposes commands for running migrations

## Environment Variables
- DB_HOST
- DB_PORT
- DB_USER
- DB_PASSWORD
- DB_NAME

## Commands
- `npm run migration:run` - Run all pending migrations
- `npm run migration:revert` - Revert the last migration

---

This service is intended to be used as a microservice in the existing Docker Compose setup.
