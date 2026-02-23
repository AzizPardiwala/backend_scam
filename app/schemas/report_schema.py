from pydantic import BaseModel

class ScamRequest(BaseModel):
    message: str


class ScamResponse(BaseModel):
    is_scam: bool
    confidence: float
    explanation: str
