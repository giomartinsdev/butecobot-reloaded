import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity({ name: "user_bet" })
export class UserBet {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column()
    userId!: string;

    @Column()
    betEventId!: string;

    @Column()
    chosenOption!: number;

    @Column()
    amount!: number;
    
    @CreateDateColumn()
    createdAt!: Date;

    @UpdateDateColumn()
    updatedAt!: Date;
}
