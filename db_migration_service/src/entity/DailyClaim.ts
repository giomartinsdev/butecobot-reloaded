import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity({ name: "daily_claim" })
export class DailyClaim {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ type: "uuid" })
    clientId!: string;

    @Column({ type: "uuid" })
    balanceOperationId!: string;

    @Column({ type: "integer" })
    amount!: number;

    @Column({ type: "text" })
    description!: string;

    @CreateDateColumn()
    createdAt!: Date;

    @UpdateDateColumn()
    updatedAt!: Date;
}
