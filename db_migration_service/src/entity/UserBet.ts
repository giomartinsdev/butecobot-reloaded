import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity({ name: "user_bet" })
export class UserBet {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    userId!: string;

    @Column()
    betEventId!: number;

    @Column()
    chosenOption!: number;

    @Column()
    amount!: number;
    
    @CreateDateColumn()
    createdAt!: Date;

    @UpdateDateColumn()
    updatedAt!: Date;
}
