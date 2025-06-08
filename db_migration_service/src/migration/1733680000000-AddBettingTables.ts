import { MigrationInterface, QueryRunner } from "typeorm";

export class AddBettingTables1733680000000 implements MigrationInterface {
    name = 'AddBettingTables1733680000000'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "bet_event" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "title" character varying NOT NULL, "description" character varying, "option1" character varying NOT NULL, "option2" character varying NOT NULL, "isActive" boolean NOT NULL DEFAULT true, "isFinished" boolean NOT NULL DEFAULT false, "winningOption" integer, "totalBetAmount" integer NOT NULL DEFAULT '0', "option1BetAmount" integer NOT NULL DEFAULT '0', "option2BetAmount" integer NOT NULL DEFAULT '0', "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_bet_event_id" PRIMARY KEY ("id"))`);
        await queryRunner.query(`CREATE TABLE "user_bet" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "userId" character varying NOT NULL, "betEventId" character varying NOT NULL, "chosenOption" integer NOT NULL, "amount" integer NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_user_bet_id" PRIMARY KEY ("id"))`);
        await queryRunner.query(`CREATE INDEX "IDX_user_bet_userId" ON "user_bet" ("userId") `);
        await queryRunner.query(`CREATE INDEX "IDX_user_bet_betEventId" ON "user_bet" ("betEventId") `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP INDEX "IDX_user_bet_betEventId"`);
        await queryRunner.query(`DROP INDEX "IDX_user_bet_userId"`);
        await queryRunner.query(`DROP TABLE "user_bet"`);
        await queryRunner.query(`DROP TABLE "bet_event"`);
    }

}
