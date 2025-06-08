from pydantic import BaseModel

class BalanceOperationCreate(BaseModel):
    receiver_id: str
    sender_id: str
    amount: int
    description: str
