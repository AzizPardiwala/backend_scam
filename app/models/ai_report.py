from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.core.database import Base


class AIReport(Base):
    __tablename__ = "ai_reports"

    id              = Column(Integer, primary_key=True, index=True)
    submission_id   = Column(Integer, ForeignKey("scam_submissions.id"), nullable=False, unique=True)
    prediction      = Column(String, nullable=True)
    confidence      = Column(Float,  nullable=True)
    scam_type       = Column(String, nullable=True)
    risk_score      = Column(Integer, nullable=True)
    reason          = Column(Text,   nullable=True)
    recommendation  = Column(Text,   nullable=True)
    generated_by    = Column(String, default="AI")
    status          = Column(String, default="DRAFT")
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))