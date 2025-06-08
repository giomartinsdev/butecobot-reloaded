# How to Create a New Migration Using Docker

This guide explains how to generate a new database migration for the `db_migration_service` using Docker Compose and TypeORM.

## Prerequisites
- Ensure your `User` entity or any other entity is updated in `src/entity/`.
- Make sure your database service (e.g., `postgres-db`) is running and accessible.

## Steps

1. **Edit your entity**
   - For example, add a new field to `User.ts`:
     ```ts
     @Column()
     surname!: string;
     ```

2. **Generate the migration**
   - Run the following command from your project root:
     ```sh
      docker-compose run --rm db-migration-service npm run migration:generate -- src/migration/FistMigration
     ```
   - Replace `FistMigration` with a descriptive name for your migration. The path must start with `src/migration/` for TypeORM to generate the file in the correct folder.
   - If you use `docker compose` (with a space), the command is the same:
     ```sh
     docker compose run --rm db-migration-service npm run migration:generate -- src/migration/AddSurnameToUser
     ```

3. **Check the generated migration**
   - The new migration file will appear in `db_migration_service/src/migration/`.

4. **Apply the migration** [[Optional]]
   - To run all pending migrations:
     ```sh
     docker-compose run --rm db-migration-service npm run migration:run
     ```

## Important: Make migrations visible on your host
- To ensure generated migration files appear on your local filesystem, add this to your `docker-compose.yml` under the `db-migration-service` service:
  ```yaml
  volumes:
    - ./db_migration_service/src/migration:/app/src/migration
  ```
- This mounts the migration folder from the container to your host, so any new migration files created in Docker will show up in your project.

## Notes
- The `--rm` flag cleans up the container after the command runs.
- The migration will be generated based on the difference between your current database schema and your entity definitions.
- Make sure your database is accessible from the container (host should be `postgres-db` if using the default setup).

---

For more details, see the TypeORM documentation: https://typeorm.io/migrations
