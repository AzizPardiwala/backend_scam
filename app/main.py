from fastapi import FastAPI
from app.core.database import engine, Base
from app.routes import health, scam
from app.models import report  # VERY IMPORTANT (registers model)

app = FastAPI(
    title="Scam Detection API",
    version="0.1.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(health.router)
app.include_router(scam.router)

# Root endpoint (required for Render health check)
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Scam Detection API is live"
    }