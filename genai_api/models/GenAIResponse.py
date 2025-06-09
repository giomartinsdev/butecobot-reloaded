from pydantic import BaseModel

class GenAIResponse(BaseModel):
    response: str
