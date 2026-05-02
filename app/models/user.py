from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)  # ✅ ADD THIS
    password = Column(String)
    name = Column(String)

    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)