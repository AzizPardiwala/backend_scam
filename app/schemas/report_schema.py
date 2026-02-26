from pydantic import BaseModel
from datetime import datetime

class ScamReportCreate(BaseModel):
    message: str

class ScamReportResponse(BaseModel):
    id: int
    message: str
    label: str
    score: int
    created_at: datetime

    class Config:
        from_attributes = True