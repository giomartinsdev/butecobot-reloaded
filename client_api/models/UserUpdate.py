from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    discordId: Optional[str] = None
    name: Optional[str] = None
