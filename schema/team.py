from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class TeamCreate(BaseModel):
    name: str
    role: str  # manager | staff
    gender: str | None = None
    email: EmailStr | None = None
    contact: str | None = None
    emergency_contact: str | None = None
    address: str | None = None

class TeamUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    gender: str | None = None
    email: EmailStr | None = None
    contact: str | None = None
    emergency_contact: str | None = None
    address: str | None = None

class TeamResponse(BaseModel):
    id: UUID
    name: str
    role: str
    email: EmailStr | None
    contact: str | None
    created_at: datetime

    class Config:
        from_attributes = True
