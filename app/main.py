from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import engine, SessionLocal
from app.models.report import ScamReport
from app.services.detector import detect_scam  # your existing logic
from sqlalchemy.sql import func
from app.core.database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


# -------------------------
# DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Request Schema
# -------------------------
class MessageRequest(BaseModel):
    message: str


# -------------------------
# Analyze Scam + Save
# -------------------------
@app.post("/analyze")
def analyze_message(request: MessageRequest, db: Session = Depends(get_db)):

    # Run your scam detection logic
    result = detect_scam(request.message)

    # Save to PostgreSQL
    new_report = ScamReport(
        message=request.message,
        label=result["label"],
        score=result["score"]
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "id": new_report.id,
        "message": new_report.message,
        "label": new_report.label,
        "score": new_report.score,
        "created_at": new_report.created_at
    }


# -------------------------
# Get All Reports
# -------------------------
@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    return db.query(ScamReport).all()


# -------------------------
# Health
# -------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}