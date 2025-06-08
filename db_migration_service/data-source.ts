import { DataSource } from "typeorm";
import { User } from "./src/entity/User";
import { BalanceOperation } from "./src/entity/BalanceOperation";
import * as dotenv from "dotenv";
dotenv.config();

// Only export a single DataSource instance as default for TypeORM CLI compatibility
export default new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "localhost",
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER || "economyuser",
    password: process.env.DB_PASSWORD || "economypass",
    database: process.env.DB_NAME || "economydb",
    synchronize: false,
    logging: false,
    entities: [User, BalanceOperation],
    migrations: ["src/migration/**/*.ts"],
    subscribers: [],
});
