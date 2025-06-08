from pydantic import BaseModel

class BetFinalize(BaseModel):
    betEventId: str
    winningOption: int  # 1 or 2
