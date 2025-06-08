import { MigrationInterface, QueryRunner } from "typeorm";

export class FistMigration1749414725393 implements MigrationInterface {
    name = 'FistMigration1749414725393'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "daily_claim" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "clientId" uuid NOT NULL, "balanceOperationId" uuid NOT NULL, "amount" integer NOT NULL, "description" text NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_f4c05aef9a9674463af9efede58" PRIMARY KEY ("id"))`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`DROP TABLE "daily_claim"`);
    }

}
