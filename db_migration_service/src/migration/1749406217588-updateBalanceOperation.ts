import { MigrationInterface, QueryRunner } from "typeorm";

export class UpdateBalanceOperation1749406217588 implements MigrationInterface {
    name = 'UpdateBalanceOperation1749406217588'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "balance_operation" DROP COLUMN "receiverId"`);
        await queryRunner.query(`ALTER TABLE "balance_operation" DROP COLUMN "senderId"`);
        await queryRunner.query(`ALTER TABLE "balance_operation" ADD "clientId" uuid NOT NULL`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "balance_operation" DROP COLUMN "clientId"`);
        await queryRunner.query(`ALTER TABLE "balance_operation" ADD "senderId" uuid NOT NULL`);
        await queryRunner.query(`ALTER TABLE "balance_operation" ADD "receiverId" uuid NOT NULL`);
    }

}
