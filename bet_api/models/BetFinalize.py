from pydantic import BaseModel

class BetFinalize(BaseModel):
    betEventId: int
    winningOption: int  # 1 or 2
