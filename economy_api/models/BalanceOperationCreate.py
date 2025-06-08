from pydantic import BaseModel

class BalanceOperationCreate(BaseModel):
    clientId: str 
    amount: int
    description: str
