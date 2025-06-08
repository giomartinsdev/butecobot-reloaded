from fastapi import FastAPI, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models.BalanceOperationCreate import BalanceOperationCreate
from models.BalanceOperation import BalanceOperation
from models.TransactionCreate import TransactionCreate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.post("/balance/add")
def add_balance_operation(op: BalanceOperationCreate):
    db: Session = SessionLocal()
    try:
        balance_op = BalanceOperation(
            clientId=op.clientId,
            amount=abs(op.amount),
            description=op.description
        )
        db.add(balance_op)
        db.commit()
        db.refresh(balance_op)
        return balance_op
    finally:
        db.close()

@app.post("/balance/subtract")
def subtract_balance_operation(op: BalanceOperationCreate):
    db: Session = SessionLocal()
    try:
        op.amount = -abs(op.amount)
        balance_op = BalanceOperation(**op.dict())
        db.add(balance_op)
        db.commit()
        db.refresh(balance_op)
        return balance_op
    finally:
        db.close()

@app.post("/balance/transaction")
def create_transaction(transaction: TransactionCreate):
    db: Session = SessionLocal()
    try:
        if transaction.senderId == transaction.receiverId:
            raise HTTPException(status_code=400, detail="Sender and receiver cannot be the same")

        sender_op = BalanceOperation(
            clientId=transaction.senderId,
            amount=-abs(transaction.amount),
            description=f"Transaction to {transaction.receiverId}: {transaction.description}"
        )
        receiver_op = BalanceOperation(
            clientId=transaction.receiverId,
            amount=abs(transaction.amount),
            description=f"Transaction from {transaction.senderId}: {transaction.description}"
        )
        db.add(sender_op)
        db.add(receiver_op)
        db.commit()
        db.refresh(sender_op)
        db.refresh(receiver_op)

        return {"sender": sender_op, "receiver": receiver_op}

    finally:
        db.close()

@app.get("/balance/{user_id}")
def get_user_balance(user_id: str):
    db: Session = SessionLocal()
    try:
        ops = db.query(BalanceOperation).filter(BalanceOperation.clientId == user_id).with_entities(BalanceOperation.amount)
        balance = sum([op.amount for op in ops])
        return {"user_id": user_id, "balance": balance}
    finally:
        db.close()

@app.get("/balance/operations/{user_id}")
def get_user_operations(user_id: str):
    db: Session = SessionLocal()
    try:
        ops = db.query(BalanceOperation).filter(BalanceOperation.clientId == user_id).all()
        return ops
    finally:
        db.close()
