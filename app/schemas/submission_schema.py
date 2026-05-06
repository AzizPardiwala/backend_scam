from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubmissionCreate(BaseModel):
    message: str


class SubmissionUpdate(BaseModel):
    message: str


class SubmissionResponse(BaseModel):
    id:         int
    user_id:    int
    message:    str
    status:     str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    