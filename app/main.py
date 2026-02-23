from fastapi import FastAPI
from app.routes import scam

app = FastAPI(title="Scam Detection API")

app.include_router(scam.router)


@app.get("/health")
def health():
    return {"status": "ok"}
