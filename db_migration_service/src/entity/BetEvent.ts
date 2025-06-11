import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity({ name: "bet_event" })
export class BetEvent {
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    title!: string;

    @Column({ nullable: true })
    description?: string;

    @Column()
    option1!: string;

    @Column()
    option2!: string;

    @Column({ default: true })
    isActive!: boolean;

    @Column({ default: false })
    isFinished!: boolean;

    @Column({ nullable: true })
    winningOption?: number;

    @Column({ default: 0 })
    totalBetAmount!: number;

    @Column({ default: 0 })
    option1BetAmount!: number;

    @Column({ default: 0 })
    option2BetAmount!: number;
    
    @CreateDateColumn()
    createdAt!: Date;

    @UpdateDateColumn()
    updatedAt!: Date;
}
