from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer
import uuid
from datetime import datetime

Base = declarative_base()

class UserBet(Base):
    __tablename__ = "user_bet"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String, nullable=False)
    betEventId = Column(Integer, nullable=False)
    chosenOption = Column(Integer, nullable=False)  # 1 or 2
    amount = Column(Integer, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, userId: str, betEventId: int, chosenOption: int, amount: int):
        self.userId = userId
        self.betEventId = betEventId
        self.chosenOption = chosenOption
        self.amount = amount

    def __repr__(self):
        return (f"UserBet(id={self.id}, userId={self.userId}, betEventId={self.betEventId}, "
                f"chosenOption={self.chosenOption}, amount={self.amount})")
