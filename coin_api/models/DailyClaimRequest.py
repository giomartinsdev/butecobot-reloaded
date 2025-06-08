from pydantic import BaseModel

class DailyClaimRequest(BaseModel):
    clientId: str
