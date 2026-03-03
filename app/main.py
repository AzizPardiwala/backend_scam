from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import report
from app.routes import scam

app = FastAPI(title="Scam Detection API")

Base.metadata.create_all(bind=engine)

app.include_router(scam.router)

@app.get("/")
def root():
    return {"message": "API running"}