from fastapi import FastAPI, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models.BalanceOperationCreate import BalanceOperationCreate
from models.BalanceOperationUpdate import BalanceOperationUpdate
from models.BalanceOperation import BalanceOperation

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.post("/balance/add", response_model=BalanceOperationCreate)
def add_balance_operation(op: BalanceOperationCreate):
    db: Session = SessionLocal()
    try:
        # Add operation for receiver (credit)
        receiver_op = BalanceOperation(**op.dict())
        db.add(receiver_op)
        # Add operation for sender (debit)
        sender_op = BalanceOperation(
            receiverId=op.sender_id,
            senderId=op.sender_id,
            amount=-abs(op.amount),
            description=op.description
        )
        db.add(sender_op)
        db.commit()
        db.refresh(receiver_op)
        db.refresh(sender_op)
        return {"receiver_op": receiver_op, "sender_op": sender_op}
    finally:
        db.close()

@app.post("/balance/subtract", response_model=BalanceOperationCreate)
def subtract_balance_operation(op: BalanceOperationCreate):
    db: Session = SessionLocal()
    try:
        # Add operation for sender (debit)
        sender_op = BalanceOperation(**op.dict())
        db.add(sender_op)
        # Add operation for receiver (credit)
        receiver_op = BalanceOperation(
            receiverId=op.receiver_id,
            senderId=op.sender_id,
            amount=abs(op.amount),
            description=op.description
        )
        db.add(receiver_op)
        db.commit()
        db.refresh(sender_op)
        db.refresh(receiver_op)
        return {"sender_op": sender_op, "receiver_op": receiver_op}
    finally:
        db.close()

@app.get("/balance/{user_id}")
def get_user_balance(user_id: str):
    db: Session = SessionLocal()
    try:
        received = db.query(BalanceOperation).filter(BalanceOperation.receiverId == user_id).with_entities(BalanceOperation.amount)
        sent = db.query(BalanceOperation).filter(BalanceOperation.senderId == user_id).with_entities(BalanceOperation.amount)
        received_sum = sum([op.amount for op in received])
        sent_sum = sum([op.amount for op in sent])
        return {"user_id": user_id, "balance": received_sum - sent_sum}
    finally:
        db.close()

@app.get("/balance/operations/{user_id}", response_model=List[BalanceOperationCreate])
def get_user_operations(user_id: str):
    db: Session = SessionLocal()
    try:
        ops = db.query(BalanceOperation).filter((BalanceOperation.receiverId == user_id) | (BalanceOperation.senderId == user_id)).all()
        return ops
    finally:
        db.close()

@app.put("/balance/operation/{operation_id}")
def update_balance_operation(operation_id: str, op: BalanceOperationUpdate):
    db: Session = SessionLocal()
    try:
        balance_op = db.query(BalanceOperation).filter(BalanceOperation.id == operation_id).first()
        if not balance_op:
            raise HTTPException(status_code=404, detail="Operation not found")
        if op.amount is not None:
            balance_op.amount = op.amount
        if op.description is not None:
            balance_op.description = op.description
        db.commit()
        db.refresh(balance_op)
        return balance_op
    finally:
        db.close()

@app.post("/balance/transaction")
def create_transaction(sender_id: str, receiver_id: str, amount: int, description: str):
    db: Session = SessionLocal()
    try:
        # Create debit for sender
        sender_op = BalanceOperation(
            receiverId=sender_id,  # self for sender
            senderId=sender_id,
            amount=-abs(amount),
            description=description
        )
        # Create credit for receiver
        receiver_op = BalanceOperation(
            receiverId=receiver_id,
            senderId=sender_id,
            amount=abs(amount),
            description=description
        )
        db.add(sender_op)
        db.add(receiver_op)
        db.commit()
        db.refresh(sender_op)
        db.refresh(receiver_op)
        return {"sender_op": sender_op, "receiver_op": receiver_op}
    finally:
        db.close()
