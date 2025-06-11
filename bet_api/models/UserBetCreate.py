from pydantic import BaseModel

class UserBetCreate(BaseModel):
    userId: str
    betEventId: int
    chosenOption: int  # 1 or 2
    amount: int
