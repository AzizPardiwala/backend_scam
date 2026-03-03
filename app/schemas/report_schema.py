from pydantic import BaseModel
from datetime import datetime

class ReportCreate(BaseModel):
    message: str

class ReportResponse(BaseModel):
    id: int
    message: str
    label: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True