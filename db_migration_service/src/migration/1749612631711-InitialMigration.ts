import { MigrationInterface, QueryRunner } from "typeorm";

export class InitialMigration1749612631711 implements MigrationInterface {
    name = 'InitialMigration1749612631711'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "user" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "discordId" character varying NOT NULL, "name" character varying NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "UQ_13af5754f14d8d255fd9b3ee5c7" UNIQUE ("discordId"), CONSTRAINT "PK_cace4a159ff9f2512dd42373760" PRIMARY KEY ("id"))`);
        await queryRunner.query(`CREATE TABLE "balance_operation" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "clientId" uuid NOT NULL, "amount" integer NOT NULL, "description" text NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_8cb82ba3c5dd568479da6ddab04" PRIMARY KEY ("id"))`);
        await queryRunner.query(`CREATE TABLE "daily_claim" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "clientId" uuid NOT NULL, "balanceOperationId" uuid NOT NULL, "amount" integer NOT NULL, "description" text NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_f4c05aef9a9674463af9efede58" PRIMARY KEY ("id"))`);
        await queryRunner.query(`CREATE TABLE "bet_event" ("id" SERIAL NOT NULL, "title" character varying NOT NULL, "description" character varying, "option1" character varying NOT NULL, "option2" character varying NOT NULL, "isActive" boolean NOT NULL DEFAULT true, "isFinished" boolean NOT NULL DEFAULT false, "winningOption" integer, "totalBetAmount" integer NOT NULL DEFAULT '0', "option1BetAmount" integer NOT NULL DEFAULT '0', "option2BetAmount" integer NOT NULL DEFAULT '0', "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_d0db616ca49c322e9b1b01f94c0" PRIMARY KEY ("id"))`);
        await queryRunner.query(`CREATE TABLE "user_bet" ("id" SERIAL NOT NULL, "userId" character varying NOT NULL, "betEventId" integer NOT NULL, "chosenOption" integer NOT NULL, "amount" integer NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_bfbb2b2bd801c8803f2b6537c45" PRIMARY KEY ("id"))`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "user_bet"`);
        await queryRunner.query(`DROP TABLE "bet_event"`);
        await queryRunner.query(`DROP TABLE "daily_claim"`);
        await queryRunner.query(`DROP TABLE "balance_operation"`);
        await queryRunner.query(`DROP TABLE "user"`);
    }

}
