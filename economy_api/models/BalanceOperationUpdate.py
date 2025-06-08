from pydantic import BaseModel
from typing import Optional

class BalanceOperationUpdate(BaseModel):
    amount: Optional[int] = None
    description: Optional[str] = None
