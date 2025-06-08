from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    discordId = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, discordId={self.discordId}, name={self.name}, createdAt={self.createdAt}, updatedAt={self.updatedAt})"


