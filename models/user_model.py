# models/user_model.py

import uuid
from datetime import datetime
from uuid import UUID as UUID_TYPE

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from pydantic import BaseModel, EmailStr

from core.database import Base


# =========================
# SQLALCHEMY MODEL (DB)
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    role = Column(String, nullable=False, default="owner")
    # owner | manager | staff | admin

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# =========================
# PYDANTIC SCHEMAS (API)
# =========================

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID_TYPE
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True  # REQUIRED for SQLAlchemy (Pydantic v2)
