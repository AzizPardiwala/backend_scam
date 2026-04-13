from fastapi import FastAPI
from app.core.database import Base, engine

from app.routes import auth, scam, report, health


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scam Detection API 🚀")

app.include_router(auth.router, prefix="/auth")
app.include_router(scam.router, prefix="/scam")
app.include_router(report.router, prefix="/reports")
app.include_router(health.router, prefix="/health")