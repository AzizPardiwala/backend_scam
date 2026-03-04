from fastapi import FastAPI
from app.core.database import engine, Base
from app.routes import report_routes  # make sure this matches your file name
from app.models import report  # ensures model is registered

app = FastAPI(
    title="Scam Detection API",
    version="0.1.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include report routes
app.include_router(report_routes.router)

# Root endpoint (VERY IMPORTANT for Render health check)
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Scam Detection API is live"
    }

# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }