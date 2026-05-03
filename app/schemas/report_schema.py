from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportCreate(BaseModel):
    message: str


class ReportUpdate(BaseModel):
    message: str


class ReportResponse(BaseModel):
    id: int
    user_id: int
    message: str
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    scam_type: Optional[str] = None
    risk_score: Optional[int] = None
    reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True