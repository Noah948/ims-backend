# models/user.py

from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, EmailStr

# IMPORT the Base from your database file (IMPORTANT)
from core.database import Base


# -----------------------------
# SQLALCHEMY MODEL
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)


# -----------------------------
# PYDANTIC SCHEMAS
# -----------------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True
