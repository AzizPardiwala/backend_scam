from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.logger import logger

# Import all models so SQLAlchemy creates tables
from app.models.user import User
from app.models.scam_report import ScamReport

# Routers
from app.routes import auth, scam, reports, user, admin

app = FastAPI(
    title="Scam Detection API",
    description="""
## Scam Detection Platform

Report, validate, and track online scams using ML + Gemini AI.

### How it works
1. User submits a scam report via **POST /scam/report**
2. API saves it instantly and returns **202 Accepted** (synchronous)
3. ML model + Gemini AI run in the **background** (asynchronous)
4. Report status changes from `PENDING` → `VERIFIED` automatically

### Roles
- **User**: Submit, update, delete own reports
- **Admin**: View all reports, delete any, manually verify/reject
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")

app.include_router(auth.router)
app.include_router(scam.router)
app.include_router(reports.router)
app.include_router(user.router)
app.include_router(admin.router)

@app.get("/", tags=["Default"])
def root():
    return {"message": "Scam Detection API is running", "version": "2.0.0", "docs": "/docs"}

@app.get("/health", tags=["Default"])
def health_check():
    return {"status": "ok"}