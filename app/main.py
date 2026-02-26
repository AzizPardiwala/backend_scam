from fastapi import FastAPI
from app.core.database import engine, Base
from app.routes import scam

app = FastAPI(title="Scam Detection API")

# Create all database tables
Base.metadata.create_all(bind=engine)

# Health check endpoint (important for deployment)
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include routes
app.include_router(scam.router)