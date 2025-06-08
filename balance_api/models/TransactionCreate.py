from pydantic import BaseModel

class TransactionCreate(BaseModel):
    senderId: str
    receiverId: str
    amount: float
    description: str
