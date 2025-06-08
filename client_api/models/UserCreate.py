from pydantic import BaseModel

class UserCreate(BaseModel):
    discordId: str
    name: str
