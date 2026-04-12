from fastapi import FastAPI
from app.routes import health, scam, report   # ✅ add report

app = FastAPI(title="Scam Alert API 🚨")

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(scam.router, prefix="/scam", tags=["Scam Detection"])
app.include_router(report.router, prefix="/reports", tags=["Reports"])  # ✅