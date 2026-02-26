from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import report  # Important for table creation

app = FastAPI()

# Create tables in PostgreSQL
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Backend is running"}