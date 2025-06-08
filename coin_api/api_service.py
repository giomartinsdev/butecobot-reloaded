from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import requests
from datetime import date
from models.DailyClaim import DailyClaim, Base
from models.DailyClaimRequest import DailyClaimRequest

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BALANCE_API_URL = os.getenv("BALANCE_API_URL")
CLIENT_API_URL = os.getenv("CLIENT_API_URL")
DAILY_COINS_AMOUNT = int(os.getenv("DAILY_COINS_AMOUNT", 100))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/daily-coins")
def claim_daily_coins(request: DailyClaimRequest):
    db: Session = SessionLocal()
    try:
        today = date.today()
        existing_claim = db.query(DailyClaim).filter(
            DailyClaim.clientId == request.clientId,
            DailyClaim.claimDate == today
        ).first()
        
        if existing_claim:
            raise HTTPException(
                status_code=400,
                detail="Daily coins already claimed today. Come back tomorrow!"
            )
        
        try:
            client_response = requests.get(f"{CLIENT_API_URL}/client/{request.clientId}")
            if client_response.status_code == 404:
                raise HTTPException(status_code=404, detail="Client not found")
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=503, detail="Client service unavailable")
        
        try:
            add_balance_response = requests.post(
                f"{BALANCE_API_URL}/balance/add",
                json={
                    "clientId": request.clientId,
                    "amount": DAILY_COINS_AMOUNT,
                    "description": "Daily coins reward"
                }
            )
            
            if add_balance_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to add coins to balance")
                
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=503, detail="Balance service unavailable")
        
        daily_claim = DailyClaim(
            clientId=request.clientId,
            claimDate=today
        )
        
        db.add(daily_claim)
        db.commit()
        db.refresh(daily_claim)
        
        return {
            "message": "Daily coins claimed successfully!",
            "amount": DAILY_COINS_AMOUNT,
            "clientId": request.clientId,
            "claimDate": today.isoformat(),
        }
        
    finally:
        db.close()

@app.get("/daily-coins/history/{client_id}")
def get_claim_history(client_id: str, limit: int = 30):
    db: Session = SessionLocal()
    try:
        claims = db.query(DailyClaim).filter(
            DailyClaim.clientId == client_id
        ).order_by(DailyClaim.claimDate.desc()).limit(limit).all()
        
        history = []
        for claim in claims:
            history.append({
                "claimDate": claim.claimDate.isoformat(),
                "amount": 100,
                "createdAt": claim.createdAt.isoformat()
            })
        
        return {
            "clientId": client_id,
            "totalClaims": len(claims),
            "totalCoinsEarned": len(claims) * 100,
            "history": history
        }
        
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "coins-api"}
