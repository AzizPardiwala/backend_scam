from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    prediction = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)