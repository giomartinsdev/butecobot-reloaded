from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime
import uuid
from datetime import datetime

Base = declarative_base()

class BalanceOperation(Base):
    __tablename__ = "balance_operation"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clientId = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, clientId: str, amount: int, description: str):
        self.clientId = clientId
        self.amount = amount
        self.description = description

    def __repr__(self):
        return (f"BalanceOperation(id={self.id}, clientId={self.clientId}, "
                f"amount={self.amount}, description={self.description}, "
                f"createdAt={self.createdAt}, updatedAt={self.updatedAt})")
