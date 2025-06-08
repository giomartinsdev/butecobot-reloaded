from pydantic import BaseModel

class UserBetCreate(BaseModel):
    userId: str
    betEventId: str
    chosenOption: int  # 1 or 2
    amount: int
