from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Text
import uuid
from datetime import datetime

Base = declarative_base()

class DailyClaim(Base):
    __tablename__ = "daily_claim"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clientId = Column(String, nullable=False)
    balanceOperationId = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return (f"DailyClaim(id={self.id}, clientId={self.clientId}, "
                f"balanceOperationId={self.balanceOperationId}, amount={self.amount}, "
                f"description={self.description}, createdAt={self.createdAt}, "
                f"updatedAt={self.updatedAt})")
