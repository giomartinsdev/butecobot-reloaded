import { DataSource } from "typeorm";
import { User } from "./src/entity/User";
import { BalanceOperation } from "./src/entity/BalanceOperation";
import { DailyClaim } from "./src/entity/DailyClaim";
import { BetEvent } from "./src/entity/BetEvent";
import { UserBet } from "./src/entity/UserBet";
import * as dotenv from "dotenv";
dotenv.config();

// Only export a single DataSource instance as default for TypeORM CLI compatibility
export default new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "localhost",
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    synchronize: false,
    logging: false,
    entities: [User, BalanceOperation, DailyClaim, BetEvent, UserBet],
    migrations: ["src/migration/**/*.ts"],
    subscribers: [],
});
