from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.core.database import Base


class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    prediction = Column(String)
    confidence = Column(Float)

    # ✅ Timezone-aware timestamp (BEST PRACTICE)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )