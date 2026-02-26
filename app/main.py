from fastapi import FastAPI
from app.core.database import engine
from app.models import scam_report
from app.routes import scam

app = FastAPI(title="Scam Detection API")

# Create tables
scam_report.Base.metadata.create_all(bind=engine)

app.include_router(scam.router)