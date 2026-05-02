from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.scam_report import ScamReport

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_reports(db: Session = Depends(get_db)):
    return db.query(ScamReport).all()