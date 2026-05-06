from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AIReportAdminUpdate(BaseModel):
    """Admin can override any AI-generated field."""
    prediction:     Optional[str] = None
    confidence:     Optional[float] = None
    scam_type:      Optional[str] = None
    risk_score:     Optional[int] = None
    reason:         Optional[str] = None
    recommendation: Optional[str] = None
    status:         Optional[str] = None    # DRAFT | PUBLISHED | REJECTED


class AIReportResponse(BaseModel):
    id:             int
    submission_id:  int
    prediction:     Optional[str] = None
    confidence:     Optional[float] = None
    scam_type:      Optional[str] = None
    risk_score:     Optional[int] = None
    reason:         Optional[str] = None
    recommendation: Optional[str] = None
    generated_by:   str
    status:         str
    created_at:     datetime
    updated_at:     datetime

    model_config = {"from_attributes": True}

    