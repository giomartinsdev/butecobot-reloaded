from pydantic import BaseModel
from typing import Optional

class GenAIRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
