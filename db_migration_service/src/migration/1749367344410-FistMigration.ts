import { MigrationInterface, QueryRunner } from "typeorm";

export class FistMigration1749367344410 implements MigrationInterface {
    name = 'FistMigration1749367344410'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "balance_operation" ("id" uuid NOT NULL DEFAULT uuid_generate_v4(), "receiverId" uuid NOT NULL, "senderId" uuid NOT NULL, "amount" integer NOT NULL, "description" text NOT NULL, "createdAt" TIMESTAMP NOT NULL DEFAULT now(), "updatedAt" TIMESTAMP NOT NULL DEFAULT now(), CONSTRAINT "PK_8cb82ba3c5dd568479da6ddab04" PRIMARY KEY ("id"))`);
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "surname"`);
        await queryRunner.query(`ALTER TABLE "user" ADD "discordId" character varying NOT NULL`);
        await queryRunner.query(`ALTER TABLE "user" ADD CONSTRAINT "UQ_13af5754f14d8d255fd9b3ee5c7" UNIQUE ("discordId")`);
        await queryRunner.query(`ALTER TABLE "user" ADD "createdAt" TIMESTAMP NOT NULL DEFAULT now()`);
        await queryRunner.query(`ALTER TABLE "user" ADD "updatedAt" TIMESTAMP NOT NULL DEFAULT now()`);
        await queryRunner.query(`ALTER TABLE "user" DROP CONSTRAINT "user_pkey"`);
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "id"`);
        await queryRunner.query(`ALTER TABLE "user" ADD "id" uuid NOT NULL DEFAULT uuid_generate_v4()`);
        await queryRunner.query(`ALTER TABLE "user" ADD CONSTRAINT "PK_cace4a159ff9f2512dd42373760" PRIMARY KEY ("id")`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "user" DROP CONSTRAINT "PK_cace4a159ff9f2512dd42373760"`);
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "id"`);
        await queryRunner.query(`ALTER TABLE "user" ADD "id" SERIAL NOT NULL`);
        await queryRunner.query(`ALTER TABLE "user" ADD CONSTRAINT "user_pkey" PRIMARY KEY ("id")`);
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "updatedAt"`);
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "createdAt"`);
        await queryRunner.query(`ALTER TABLE "user" DROP CONSTRAINT "UQ_13af5754f14d8d255fd9b3ee5c7"`);
        await queryRunner.query(`ALTER TABLE "user" DROP COLUMN "discordId"`);
        await queryRunner.query(`ALTER TABLE "user" ADD "surname" character varying NOT NULL`);
        await queryRunner.query(`DROP TABLE "balance_operation"`);
    }

}
