from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class ScamReport(Base):
    __tablename__ = "scam_reports"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    status = Column(String, default="pending")
