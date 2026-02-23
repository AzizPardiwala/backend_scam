# from sqlalchemy import Column, Integer, String, DateTime
# from datetime import datetime, timezone
# from app.core.database import Base

# class ScamReportDB(Base):
#     __tablename__ = "scam_reports"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     description = Column(String, nullable=False)
#     amount_lost = Column(Integer, nullable=True)
#     location = Column(String, nullable=True)
#     reported_at = Column(
#         DateTime(timezone=True),
#         default=lambda: datetime.now(timezone.utc)
#     )
