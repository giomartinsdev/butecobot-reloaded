import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";

@Entity({ name: "user" })
export class User {
    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ unique: true })
    discordId!: string;

    @Column()
    name!: string;
    
    @CreateDateColumn()
    createdAt!: Date;

    @UpdateDateColumn()
    updatedAt!: Date;
}
