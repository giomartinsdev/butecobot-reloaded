from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import requests
import logging
import uuid
from datetime import date, timedelta
from models.DailyClaim import DailyClaim, Base
from models.DailyClaimRequest import DailyClaimRequest
from sqlalchemy import func

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
BALANCE_API_URL = os.getenv("BALANCE_API_URL")
CLIENT_API_URL = os.getenv("CLIENT_API_URL")
DAILY_COINS_AMOUNT = int(os.getenv("DAILY_COINS_AMOUNT", 100))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/daily-coins")
def claim_daily_coins(request: DailyClaimRequest):
    logger.info(f"Daily coin claim attempt by client: {request.clientId}")
    db: Session = SessionLocal()
    try:
        today = date.today()
        existing_claim = db.query(DailyClaim).filter(
            DailyClaim.clientId == request.clientId,
            func.date(DailyClaim.createdAt) == today
        ).first()
        
        if existing_claim:
            logger.warning(f"Daily coins already claimed today by client: {request.clientId}")
            raise HTTPException(
                status_code=400,
                detail="Daily coins already claimed today. Come back tomorrow!"
            )
        
        try:
            client_response = requests.get(f"{CLIENT_API_URL}/client/{request.clientId}")
            if client_response.status_code == 404:
                logger.warning(f"Daily coin claim failed - client not found: {request.clientId}")
                raise HTTPException(status_code=404, detail="Client not found")
        except requests.exceptions.RequestException:
            logger.error(f"Client service unavailable during daily coin claim for: {request.clientId}")
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
                logger.error(f"Failed to add daily coins to balance for client: {request.clientId}")
                raise HTTPException(status_code=500, detail="Failed to add coins to balance")
            
            balance_response_data = add_balance_response.json()
            balance_operation_id = balance_response_data.get('id', str(uuid.uuid4()))
                
        except requests.exceptions.RequestException:
            logger.error(f"Balance service unavailable during daily coin claim for: {request.clientId}")
            raise HTTPException(status_code=503, detail="Balance service unavailable")
        
        daily_claim = DailyClaim(
            clientId=request.clientId,
            balanceOperationId=balance_operation_id,
            amount=DAILY_COINS_AMOUNT,
            description="Daily coins reward"
        )
        
        db.add(daily_claim)
        db.commit()
        db.refresh(daily_claim)
        
        logger.info(f"Successfully processed daily coin claim for client {request.clientId}: +{DAILY_COINS_AMOUNT} coins")
        
        return {
            "message": "Daily coins claimed successfully!",
            "amount": DAILY_COINS_AMOUNT,
            "clientId": request.clientId,
            "claimDate": today.isoformat(),
            "balanceOperationId": balance_operation_id
        }
        
    finally:
        db.close()

@app.get("/daily-coins/history/{client_id}")
def get_claim_history(client_id: str, limit: int = 30):
    logger.info(f"Getting daily coin claim history for client: {client_id} (limit: {limit})")
    db: Session = SessionLocal()
    try:
        claims = db.query(DailyClaim).filter(
            DailyClaim.clientId == client_id
        ).order_by(DailyClaim.createdAt.desc()).limit(limit).all()
        
        history = []
        total_earned = 0
        for claim in claims:
            claim_amount = claim.amount
            total_earned += claim_amount
            history.append({
                "claimDate": claim.createdAt.date().isoformat(),
                "amount": claim_amount,
                "description": claim.description,
                "createdAt": claim.createdAt.isoformat()
            })
        
        logger.info(f"Retrieved {len(history)} claim records for client: {client_id}")
        return {
            "clientId": client_id,
            "totalClaims": len(claims),
            "totalCoinsEarned": total_earned,
            "history": history
        }
        
    finally:
        db.close()

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "service": "coins-api"}

@app.get("/daily-coins/status/{client_id}")
def get_claim_status(client_id: str):
    """Check if user can claim daily coins today."""
    logger.info(f"Checking daily coin claim status for client: {client_id}")
    db: Session = SessionLocal()
    try:
        today = date.today()
        from sqlalchemy import func
        existing_claim = db.query(DailyClaim).filter(
            DailyClaim.clientId == client_id,
            func.date(DailyClaim.createdAt) == today
        ).first()
        
        can_claim = existing_claim is None
        next_claim_date = (today + timedelta(days=1)).isoformat() if not can_claim else today.isoformat()
        
        return {
            "clientId": client_id,
            "canClaim": can_claim,
            "lastClaimDate": existing_claim.createdAt.date().isoformat() if existing_claim else None,
            "nextClaimDate": next_claim_date,
            "dailyAmount": DAILY_COINS_AMOUNT
        }
        
    finally:
        db.close()
