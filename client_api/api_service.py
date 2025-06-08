from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models.User import User
from models.UserCreate import UserCreate
from models.UserUpdate import UserUpdate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.post("/client/")
def register_client(user: UserCreate):
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.discordId == user.discordId).first()
        if existing:
            raise HTTPException(status_code=409, detail="User already registered")
        new_user = User(
            discordId=user.discordId,
            name=user.name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()

@app.get("/client/")
def get_all_clients():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        return users
    finally:
        db.close()

@app.get("/client/{id}")
def get_client(id: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()

@app.get("/client/discordId/{discord_id}")
def get_client_by_discordId(discord_id: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.discordId == discord_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()

@app.put("/client/{id}")
def update_client(id: str, user: UserUpdate):
    db: Session = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.id == id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.discordId is not None:
            existing_user.discordId = user.discordId
        if user.name is not None:
            existing_user.name = user.name
        db.commit()
        db.refresh(existing_user)
        return existing_user
    finally:
        db.close()

@app.delete("/client/{id}")
def delete_client(id: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"detail": "User deleted"}
    finally:
        db.close()
