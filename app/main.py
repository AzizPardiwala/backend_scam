from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


# -----------------------------
# Request Model
# -----------------------------
class ReportCreate(BaseModel):
    title: str
    description: str


# -----------------------------
# Root GET
# -----------------------------
@app.get("/")
def read_root():
    return {
        "message": "Backend is running successfully 🚀",
        "timestamp": datetime.utcnow()
    }


# -----------------------------
# Root POST
# -----------------------------
@app.post("/")
def create_report(report: ReportCreate):
    return {
        "message": "Report received successfully ✅",
        "data": report,
        "created_at": datetime.utcnow()
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}