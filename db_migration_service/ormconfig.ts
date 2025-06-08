import { DataSource } from "typeorm";
import { User } from "./src/entity/User";
import * as dotenv from "dotenv";
dotenv.config();

export default new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "localhost",
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER || "economyuser",
    password: process.env.DB_PASSWORD || "economypass",
    database: process.env.DB_NAME || "economydb",
    synchronize: false,
    logging: false,
    entities: [User],
    migrations: ["src/migration/**/*.ts"],
    subscribers: [],
});
