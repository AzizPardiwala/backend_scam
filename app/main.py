from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.logger import logger

# Import ALL models so SQLAlchemy creates their tables on startup
from app.models.user import User
from app.models.scam_report import ScamReport       # kept for backward compat
from app.models.submission import ScamSubmission
from app.models.ai_report import AIReport

# Routers
from app.routes import auth, user, admin
from app.routes import submissions, ai_reports
from app.routes import reports                       # public feed (kept)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready")
    except Exception as e:
        logger.error(f"DB startup error: {e}")
        logger.warning("Could not connect to DB — check DATABASE_URL")
    yield
    # ── Shutdown ─────────────────────────────────────────────
    logger.info("App shutting down")


app = FastAPI(
    title="Scam Detection API",
    description="""
## Scam Detection Platform

Report, validate, and track online scams using ML + Gemini AI.

### How it works
1. **User** submits scam text → `POST /submissions/`
2. API saves it **instantly** → returns `202 Accepted` *(synchronous)*
3. **ML + Gemini AI** run in the background *(asynchronous)*
4. An **AI Report** is created and linked to the submission
5. **User** can view their report → `GET /submissions/{id}/report`
6. **Admin** can edit, override, publish, or reject reports

### Two separate APIs
| API | Who manages it | Purpose |
|-----|---------------|---------|
| `/submissions` | User | Raw scam text submitted by users |
| `/ai-reports` | Admin only | AI-generated analysis reports |

### Roles
- **User** — submit, update, delete own submissions. Read own report.
- **Admin** — full control over all submissions and reports.
    """,
    version="3.0.0",
    lifespan=lifespan,
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

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(submissions.router)
app.include_router(ai_reports.router)
app.include_router(reports.router)      # public feed — kept for backward compat


@app.get("/", tags=["Default"])
def root():
    return {
        "message": "Scam Detection API",
        "version": "3.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Default"])
def health_check():
    return {"status": "ok"}
