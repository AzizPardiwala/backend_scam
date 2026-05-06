from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.core.database import Base


class ScamSubmission(Base):
    __tablename__ = "scam_submissions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    message     = Column(Text, nullable=False)
    status      = Column(String, default="PENDING")   # PENDING | REVIEWED | FAILED
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    
    