from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Date
import uuid
from datetime import datetime

Base = declarative_base()

class DailyClaim(Base):
    __tablename__ = "daily_claim"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clientId = Column(String, nullable=False)
    claimDate = Column(Date, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return (f"DailyClaim(id={self.id}, clientId={self.clientId}, "
                f"claimDate={self.claimDate}, createdAt={self.createdAt})")
