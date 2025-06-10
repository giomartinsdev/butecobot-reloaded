from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging
from models.User import User
from models.UserCreate import UserCreate
from models.UserUpdate import UserUpdate

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

@app.post("/client/")
def register_client(user: UserCreate):
    logger.info(f"Attempting to register new client with discordId: {user.discordId}")
    db: Session = SessionLocal()
    try:
        logger.info(f"Checking if user already exists with discordId: {user.discordId}")
        existing = db.query(User).filter(User.discordId == user.discordId).first()
        if existing:
            logger.warning(f"User registration failed - user already exists: {user.discordId}")
            raise HTTPException(status_code=409, detail="User already registered")
        
        logger.info(f"Creating new user with discordId: {user.discordId}")
        new_user = User(
            discordId=user.discordId,
            name=user.name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Successfully registered new client: {new_user.id} ({user.discordId})")
        return new_user
    finally:
        db.close()

@app.get("/client/")
def get_all_clients():
    logger.info("Fetching all clients")
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Retrieved {len(users)} clients")
        return users
    finally:
        db.close()

@app.get("/client/{id}")
def get_client(id: str):
    logger.info(f"Fetching client by ID: {id}")
    db: Session = SessionLocal()
    try:
        logger.info(f"Querying database for client with ID: {id}")
        user = db.query(User).filter(User.id == id).first()
        if not user:
            logger.warning(f"Client not found by ID: {id}")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Successfully retrieved client: {user.id} ({user.discordId})")
        return user
    finally:
        db.close()

@app.get("/client/discordId/{discord_id}")
def get_client_by_discordId(discord_id: str):
    logger.info(f"Fetching client by Discord ID: {discord_id}")
    db: Session = SessionLocal()
    try:
        logger.info(f"Querying database for client with Discord ID: {discord_id}")
        user = db.query(User).filter(User.discordId == discord_id).first()
        if not user:
            logger.warning(f"Client not found by Discord ID: {discord_id}")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Successfully retrieved client by Discord ID: {user.id} ({discord_id})")
        return user
    finally:
        db.close()

@app.put("/client/{id}")
def update_client(id: str, user: UserUpdate):
    logger.info(f"Updating client: {id}")
    db: Session = SessionLocal()
    try:
        logger.info(f"Checking if client exists for update: {id}")
        existing_user = db.query(User).filter(User.id == id).first()
        if not existing_user:
            logger.warning(f"Cannot update - client not found: {id}")
            raise HTTPException(status_code=404, detail="User not found")
        if user.discordId is not None:
            existing_user.discordId = user.discordId
        if user.name is not None:
            existing_user.name = user.name
        db.commit()
        db.refresh(existing_user)
        logger.info(f"Successfully updated client: {id}")
        return existing_user
    finally:
        db.close()

@app.delete("/client/{id}")
def delete_client(id: str):
    logger.info(f"Deleting client: {id}")
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            logger.warning(f"Cannot delete - client not found: {id}")
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        logger.info(f"Successfully deleted client: {id}")
        return {"detail": "User deleted"}
    finally:
        db.close()

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "client-api"}
