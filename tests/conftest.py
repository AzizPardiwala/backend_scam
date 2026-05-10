import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.scam_report import ScamReport
from app.models.submission import ScamSubmission
from app.models.ai_report import AIReport
from app.main import app

# ── In-memory SQLite DB ───────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Direct DB session for unit tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app, raise_server_exceptions=False)


# ── Pre-built users ───────────────────────────────────────────────────────────

@pytest.fixture
def regular_user(db):
    user = User(
        email="user@test.com",
        password=hash_password("password123"),
        name="Test User",
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@test.com",
        password=hash_password("adminpass"),
        name="Admin User",
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(regular_user):
    return create_access_token({"user_id": regular_user.id, "role": "user"})


@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"user_id": admin_user.id, "role": "admin"})


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_report(db, regular_user):
    """Old ScamReport fixture — kept for backward compat with admin tests."""
    from app.models.scam_report import ScamReport
    report = ScamReport(
        user_id=regular_user.id,
        message="Someone called me saying I won a lottery and asked for my bank details",
        status="PENDING"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@pytest.fixture
def verified_report(db, regular_user):
    """Old ScamReport fixture — kept for backward compat with admin tests."""
    from app.models.scam_report import ScamReport
    report = ScamReport(
        user_id=regular_user.id,
        message="Fake job offer asking for registration fee of 5000 rupees",
        prediction="SCAM",
        confidence=0.95,
        scam_type="JOB_SCAM",
        risk_score=8,
        reason="Classic advance fee job scam",
        status="VERIFIED"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@pytest.fixture
def sample_submission(db, regular_user):
    """New ScamSubmission fixture for submission tests."""
    sub = ScamSubmission(
        user_id=regular_user.id,
        message="Someone called me saying I won a lottery",
        status="PENDING"
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@pytest.fixture
def reviewed_submission(db, regular_user):
    """A submission that has been reviewed with an AI report."""
    sub = ScamSubmission(
        user_id=regular_user.id,
        message="Fake job offer asking for money",
        status="REVIEWED"
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    report = AIReport(
        submission_id=sub.id,
        prediction="SCAM",
        confidence=0.95,
        scam_type="JOB_SCAM",
        risk_score=8,
        reason="Classic advance fee job scam",
        recommendation="Do not pay any registration fee",
        generated_by="AI",
        status="PUBLISHED"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return sub