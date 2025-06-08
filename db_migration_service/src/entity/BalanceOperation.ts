import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity({ name: "balance_operation" })
export class BalanceOperation {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ type: "uuid" })
    receiverId!: string;

    @Column({ type: "uuid" })
    senderId!: string;

    @Column({ type: "integer" })
    amount!: number;

    @Column({ type: "text" })
    description!: string;

    @CreateDateColumn()
    createdAt!: Date;

    @UpdateDateColumn()
    updatedAt!: Date;
}
