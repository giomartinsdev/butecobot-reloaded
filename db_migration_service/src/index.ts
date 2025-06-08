import "reflect-metadata";
import { DataSource } from "typeorm";
import { User } from "./entity/User";

export const AppDataSource = new DataSource({
    type: "postgres",
    host: process.env.DB_HOST || "localhost",
    port: parseInt(process.env.DB_PORT || "5432"),
    username: process.env.DB_USER || "economyuser",
    password: process.env.DB_PASSWORD || "economypass",
    database: process.env.DB_NAME || "economydb",
    synchronize: false,
    logging: false,
    entities: [User],
    migrations: ["dist/migration/**/*.js"],
    subscribers: [],
});

AppDataSource.initialize()
    .then(() => {
        console.log("Data Source has been initialized!");
    })
    .catch((err) => {
        console.error("Error during Data Source initialization", err);
    });
