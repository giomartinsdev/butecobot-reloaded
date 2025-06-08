from pydantic import BaseModel
from typing import Optional

class BetEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    option1: str
    option2: str
