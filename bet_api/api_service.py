from fastapi import FastAPI, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import requests
import logging
from models.BetEvent import BetEvent, Base
from models.BetEventCreate import BetEventCreate
from models.UserBet import UserBet
from models.UserBetCreate import UserBetCreate
from models.BetFinalize import BetFinalize

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
BALANCE_API_URL = os.getenv("BALANCE_API_URL")
CLIENT_API_URL = os.getenv("CLIENT_API_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "bet-api"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_user_balance(user_id: str, amount: int) -> bool:
    """Check if user has sufficient balance"""
    try:
        response = requests.get(f"{BALANCE_API_URL}/balance/{user_id}")
        if response.status_code != 200:
            return False
        balance_data = response.json()
        return balance_data.get("balance", 0) >= amount
    except Exception as e:
        logger.error(f"Error checking user balance: {e}")
        return False

def subtract_user_balance(user_id: str, amount: int, description: str) -> bool:
    """Subtract amount from user balance"""
    try:
        payload = {
            "clientId": user_id,
            "amount": amount,
            "description": description
        }
        response = requests.post(f"{BALANCE_API_URL}/balance/subtract", json=payload)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error subtracting user balance: {e}")
        return False

def add_user_balance(user_id: str, amount: int, description: str) -> bool:
    """Add amount to user balance"""
    try:
        payload = {
            "clientId": user_id,
            "amount": amount,
            "description": description
        }
        response = requests.post(f"{BALANCE_API_URL}/balance/add", json=payload)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error adding user balance: {e}")
        return False

@app.post("/bet/event")
def create_bet_event(event: BetEventCreate):
    """Create a new betting event"""
    db = SessionLocal()
    try:
        db_event = BetEvent(
            title=event.title,
            description=event.description,
            option1=event.option1,
            option2=event.option2
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        logger.info(f"Created bet event: {db_event.id}")
        return {"message": "Bet event created successfully", "eventId": db_event.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bet event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create bet event")
    finally:
        db.close()

@app.get("/bet/events")
def get_active_events():
    """Get all active betting events"""
    db = SessionLocal()
    try:
        events = db.query(BetEvent).filter(BetEvent.isActive == True, BetEvent.isFinished == False).all()
        return {
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "option1": event.option1,
                    "option2": event.option2,
                    "totalBetAmount": event.totalBetAmount,
                    "option1BetAmount": event.option1BetAmount,
                    "option2BetAmount": event.option2BetAmount,
                    "createdAt": event.createdAt
                }
                for event in events
            ]
        }
    except Exception as e:
        logger.error(f"Error getting active events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active events")
    finally:
        db.close()

@app.get("/bet/events/finished")
def get_finished_events():
    """Get all finished betting events"""
    db = SessionLocal()
    try:
        events = db.query(BetEvent).filter(BetEvent.isFinished == True).all()
        return {
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "option1": event.option1,
                    "option2": event.option2,
                    "winningOption": event.winningOption,
                    "totalBetAmount": event.totalBetAmount,
                    "option1BetAmount": event.option1BetAmount,
                    "option2BetAmount": event.option2BetAmount,
                    "createdAt": event.createdAt
                }
                for event in events
            ]
        }
    except Exception as e:
        logger.error(f"Error getting finished events: {e}")
        raise HTTPException(status_code=500, detail="Failed to get finished events")
    finally:
        db.close()

@app.post("/bet/place")
def place_bet(bet: UserBetCreate):
    """Place a bet on an event"""
    if bet.chosenOption not in [1, 2]:
        raise HTTPException(status_code=400, detail="Chosen option must be 1 or 2")
    
    if bet.amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")
    
    db = SessionLocal()
    try:
        # Check if event exists and is active
        event = db.query(BetEvent).filter(
            BetEvent.id == bet.betEventId,
            BetEvent.isActive == True,
            BetEvent.isFinished == False
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or not active")
        
        # Check if user already bet on this event
        existing_bet = db.query(UserBet).filter(
            UserBet.userId == bet.userId,
            UserBet.betEventId == bet.betEventId
        ).first()
        
        if existing_bet:
            raise HTTPException(status_code=400, detail="User already placed a bet on this event")
        
        # Check user balance
        if not check_user_balance(bet.userId, bet.amount):
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Subtract balance from user
        if not subtract_user_balance(bet.userId, bet.amount, f"Bet on {event.title}"):
            raise HTTPException(status_code=500, detail="Failed to subtract balance")
        
        # Create the bet
        db_bet = UserBet(
            userId=bet.userId,
            betEventId=bet.betEventId,
            chosenOption=bet.chosenOption,
            amount=bet.amount
        )
        db.add(db_bet)
        
        # Update event totals
        event.totalBetAmount += bet.amount
        if bet.chosenOption == 1:
            event.option1BetAmount += bet.amount
        else:
            event.option2BetAmount += bet.amount
        
        db.commit()
        db.refresh(db_bet)
        
        logger.info(f"User {bet.userId} placed bet {db_bet.id} on event {bet.betEventId}")
        return {"message": "Bet placed successfully", "betId": db_bet.id}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error placing bet: {e}")
        raise HTTPException(status_code=500, detail="Failed to place bet")
    finally:
        db.close()

@app.post("/bet/finalize")
def finalize_bet(finalize_data: BetFinalize):
    """Finalize a betting event and distribute winnings"""
    if finalize_data.winningOption not in [1, 2]:
        raise HTTPException(status_code=400, detail="Winning option must be 1 or 2")
    
    db = SessionLocal()
    try:
        # Get the event
        event = db.query(BetEvent).filter(
            BetEvent.id == finalize_data.betEventId,
            BetEvent.isActive == True,
            BetEvent.isFinished == False
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or already finished")
        
        # Get all winning bets
        winning_bets = db.query(UserBet).filter(
            UserBet.betEventId == finalize_data.betEventId,
            UserBet.chosenOption == finalize_data.winningOption
        ).all()
        
        # Calculate total winning bet amount
        winning_total = sum(bet.amount for bet in winning_bets)
        
        if winning_total == 0:
            # No winners, mark as finished
            event.isFinished = True
            event.winningOption = finalize_data.winningOption
            db.commit()
            logger.info(f"Event {event.id} finished with no winners")
            return {"message": "Event finished with no winners"}
        
        # Distribute winnings proportionally
        total_pool = event.totalBetAmount
        distributions = []
        
        for bet in winning_bets:
            # Calculate proportion of winnings
            proportion = bet.amount / winning_total
            winnings = int(total_pool * proportion)
            
            # Add winnings to user balance
            if add_user_balance(
                bet.userId, 
                winnings, 
                f"Winnings from {event.title} - Option {finalize_data.winningOption}"
            ):
                distributions.append({
                    "userId": bet.userId,
                    "originalBet": bet.amount,
                    "winnings": winnings,
                    "profit": winnings - bet.amount
                })
                logger.info(f"Distributed {winnings} to user {bet.userId}")
        
        # Mark event as finished
        event.isFinished = True
        event.winningOption = finalize_data.winningOption
        db.commit()
        
        logger.info(f"Finalized event {event.id} with {len(distributions)} winners")
        return {
            "message": "Event finalized successfully",
            "winningOption": finalize_data.winningOption,
            "totalPool": total_pool,
            "winnersCount": len(distributions),
            "distributions": distributions
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error finalizing bet: {e}")
        raise HTTPException(status_code=500, detail="Failed to finalize bet")
    finally:
        db.close()

@app.get("/bet/user/{user_id}")
def get_user_bets(user_id: str):
    """Get all bets for a specific user"""
    db = SessionLocal()
    try:
        bets = db.query(UserBet).filter(UserBet.userId == user_id).all()
        
        bet_details = []
        for bet in bets:
            event = db.query(BetEvent).filter(BetEvent.id == bet.betEventId).first()
            if event:
                bet_details.append({
                    "betId": bet.id,
                    "eventId": event.id,
                    "eventTitle": event.title,
                    "chosenOption": bet.chosenOption,
                    "chosenOptionText": event.option1 if bet.chosenOption == 1 else event.option2,
                    "amount": bet.amount,
                    "isFinished": event.isFinished,
                    "winningOption": event.winningOption,
                    "isWinner": event.isFinished and event.winningOption == bet.chosenOption,
                    "createdAt": bet.createdAt
                })
        
        return {"bets": bet_details}
        
    except Exception as e:
        logger.error(f"Error getting user bets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user bets")
    finally:
        db.close()

@app.get("/bet/event/{event_id}")
def get_event_details(event_id: str):
    """Get detailed information about a specific event"""
    db = SessionLocal()
    try:
        event = db.query(BetEvent).filter(BetEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get all bets for this event
        bets = db.query(UserBet).filter(UserBet.betEventId == event_id).all()
        
        return {
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "option1": event.option1,
                "option2": event.option2,
                "isActive": event.isActive,
                "isFinished": event.isFinished,
                "winningOption": event.winningOption,
                "totalBetAmount": event.totalBetAmount,
                "option1BetAmount": event.option1BetAmount,
                "option2BetAmount": event.option2BetAmount,
                "createdAt": event.createdAt
            },
            "totalBets": len(bets),
            "option1Bets": len([b for b in bets if b.chosenOption == 1]),
            "option2Bets": len([b for b in bets if b.chosenOption == 2])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get event details")
    finally:
        db.close()

@app.delete("/bet/event/{event_id}")
def cancel_bet_event(event_id: str):
    """Cancel a betting event and refund all bets"""
    db = SessionLocal()
    try:
        event = db.query(BetEvent).filter(
            BetEvent.id == event_id,
            BetEvent.isActive == True,
            BetEvent.isFinished == False
        ).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or already finished")
        
        # Get all bets for this event
        bets = db.query(UserBet).filter(UserBet.betEventId == event_id).all()
        
        # Refund all bets
        refunded_count = 0
        for bet in bets:
            if add_user_balance(bet.userId, bet.amount, f"Refund for cancelled event: {event.title}"):
                refunded_count += 1
                logger.info(f"Refunded {bet.amount} to user {bet.userId}")
        
        # Mark event as inactive
        event.isActive = False
        db.commit()
        
        logger.info(f"Cancelled event {event.id} and refunded {refunded_count} bets")
        return {
            "message": "Event cancelled successfully",
            "refundedBets": refunded_count,
            "totalRefunded": sum(bet.amount for bet in bets)
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling event: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel event")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
