from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.core.database import Base


class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)

    # Who posted it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # The report content
    message = Column(Text, nullable=False)

    # ML result (filled by background task)
    prediction = Column(String, nullable=True)       # "SCAM" or "NOT_SCAM"
    confidence = Column(Float, nullable=True)

    # Gemini AI result (filled by background task)
    scam_type = Column(String, nullable=True)        # e.g. "UPI_FRAUD"
    risk_score = Column(Integer, nullable=True)      # 1-10
    reason = Column(Text, nullable=True)             # AI explanation

    # Status: PENDING → VERIFIED or REJECTED
    status = Column(String, default="PENDING")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )