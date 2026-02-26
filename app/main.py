from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import SessionLocal, engine, get_db
from models import Base, ScamReport
from datetime import datetime

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# -----------------------------
# Scam Detection Logic
# -----------------------------
def detect_scam(message: str):
    scam_keywords = ["win", "lottery", "prize", "otp", "urgent", "money"]

    message_lower = message.lower()
    score = 0

    for word in scam_keywords:
        if word in message_lower:
            score += 1

    if score > 0:
        return "SCAM", score
    else:
        return "SAFE", score


# -----------------------------
# Analyze Endpoint
# -----------------------------
@app.post("/analyze")
def analyze_message(message: str, db: Session = Depends(get_db)):

    label, score = detect_scam(message)

    new_report = ScamReport(
        message=message,
        label=label,
        score=score,
        created_at=datetime.utcnow()
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report


# -----------------------------
# Reports Endpoint (WITH FILTER)
# -----------------------------
@app.get("/reports")
def get_reports(
    label: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ScamReport)

    if label:
        query = query.filter(ScamReport.label == label)

    reports = query.order_by(ScamReport.created_at.desc()).all()

    return reports