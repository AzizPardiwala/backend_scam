import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Google Auth"])

# ── Setup OAuth client ─────────────────────────────────────────
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(config)
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# ─────────────────────────────────────────────────────────────
# GET /auth/google
# Redirects user to Google login page
# ─────────────────────────────────────────────────────────────
@router.get("/google")
async def google_login(request: Request):
    """
    Step 1 — Redirect user to Google login page.
    Open this URL in browser to start Google login.
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


# ─────────────────────────────────────────────────────────────
# GET /auth/google/callback
# Google calls this after user logs in
# ─────────────────────────────────────────────────────────────
@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Step 2 — Google redirects here after login.
    We get user info from Google, create account if needed,
    and return our JWT token.
    """
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        logger.error(f"Google auth failed: {e}")
        raise HTTPException(status_code=400, detail="Google authentication failed")

    # Get user info from Google
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Could not get user info from Google")

    google_email = user_info.get("email")
    google_name = user_info.get("name", "Google User")

    logger.info(f"Google login attempt for email: {google_email}")

    # Check if user already exists in our database
    user = db.query(User).filter(User.email == google_email).first()

    if not user:
        # Option A — Create account automatically
        logger.info(f"Creating new user for Google account: {google_email}")
        user = User(
            email=google_email,
            password="GOOGLE_AUTH",   # placeholder — they never use password
            name=google_name,
            role="user",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created: {user.id}")
    else:
        # User exists — just log them in
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        logger.info(f"Existing user logged in via Google: {user.id}")

    # Create our JWT token
    token = create_access_token({"user_id": user.id, "role": user.role})

    return {
        "message": "Google login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
