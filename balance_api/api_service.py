from fastapi import FastAPI, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging
from models.BalanceOperationCreate import BalanceOperationCreate
from models.BalanceOperation import BalanceOperation
from models.TransactionCreate import TransactionCreate

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.post("/balance/add")
def add_balance_operation(op: BalanceOperationCreate):
    logger.info(f"Adding balance for client {op.clientId}: +{op.amount} ({op.description})")
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
        logger.info(f"Successfully added balance operation: {balance_op.id}")
        return balance_op
    finally:
        db.close()

@app.post("/balance/subtract")
def subtract_balance_operation(op: BalanceOperationCreate):
    logger.info(f"Subtracting balance for client {op.clientId}: -{abs(op.amount)} ({op.description})")
    db: Session = SessionLocal()
    try:
        op.amount = -abs(op.amount)
        balance_op = BalanceOperation(**op.dict())
        db.add(balance_op)
        db.commit()
        db.refresh(balance_op)
        logger.info(f"Successfully subtracted balance operation: {balance_op.id}")
        return balance_op
    finally:
        db.close()

@app.post("/balance/transaction")
def create_transaction(transaction: TransactionCreate):
    logger.info(f"Creating transaction: {transaction.senderId} -> {transaction.receiverId}, amount: {transaction.amount}")
    db: Session = SessionLocal()
    try:
        if transaction.senderId == transaction.receiverId:
            logger.warning(f"Transaction failed: sender and receiver are the same ({transaction.senderId})")
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
        
        logger.info(f"Successfully created transaction: {sender_op.id} and {receiver_op.id}")
        return {"sender": sender_op, "receiver": receiver_op}

    finally:
        db.close()

@app.get("/balance/{user_id}")
def get_user_balance(user_id: str):
    logger.info(f"Getting balance for user: {user_id}")
    db: Session = SessionLocal()
    try:
        ops = db.query(BalanceOperation).filter(BalanceOperation.clientId == user_id).with_entities(BalanceOperation.amount)
        balance = sum([op.amount for op in ops])
        logger.info(f"User {user_id} balance: {balance}")
        return {"user_id": user_id, "balance": balance}
    finally:
        db.close()

@app.get("/balance/operations/{user_id}")
def get_user_operations(user_id: str):
    logger.info(f"Getting operations for user: {user_id}")
    db: Session = SessionLocal()
    try:
        ops = db.query(BalanceOperation).filter(BalanceOperation.clientId == user_id).all()
        logger.info(f"Retrieved {len(ops)} operations for user {user_id}")
        return ops
    finally:
        db.close()

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "balance-api"}
