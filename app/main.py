from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine

# Routers
from app.routes import auth, scam, reports, user

# Create app
app = FastAPI(
    title="Scam Detection API 🚀",
    version="1.0.0"
)

# ✅ CORS (important for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)

# ✅ Include Routes
app.include_router(auth.router)
app.include_router(scam.router)
app.include_router(reports.router)
app.include_router(user.router)


# ✅ Root API
@app.get("/")
def root():
    return {
        "message": "Scam Detection API Running 🚀",
        "docs": "/docs"
    }


# ✅ Health check (important for Render)
@app.get("/health")
def health_check():
    return {"status": "ok"}