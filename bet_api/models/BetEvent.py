from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean, Integer
import uuid
from datetime import datetime

Base = declarative_base()

class BetEvent(Base):
    __tablename__ = "bet_event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    option1 = Column(String, nullable=False)
    option2 = Column(String, nullable=False)
    isActive = Column(Boolean, default=True, nullable=False)
    isFinished = Column(Boolean, default=False, nullable=False)
    winningOption = Column(Integer, nullable=True)  # 1 or 2
    totalBetAmount = Column(Integer, default=0, nullable=False)
    option1BetAmount = Column(Integer, default=0, nullable=False)
    option2BetAmount = Column(Integer, default=0, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, title: str, description: str, option1: str, option2: str):
        self.title = title
        self.description = description
        self.option1 = option1
        self.option2 = option2

    def __repr__(self):
        return (f"BetEvent(id={self.id}, title={self.title}, option1={self.option1}, "
                f"option2={self.option2}, isActive={self.isActive}, isFinished={self.isFinished})")
