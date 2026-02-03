from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class JobCreate(BaseModel):
    business_name: str
    title: str
    description: str
    location: str | None = None
    salary: str | None = None
    email: EmailStr | None = None
    contact: str | None = None

class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    salary: str | None = None
    email: EmailStr | None = None
    contact: str | None = None

class JobResponse(BaseModel):
    id: UUID
    business_name: str
    title: str
    description: str
    location: str | None
    salary: str | None
    email: EmailStr | None
    contact: str | None
    created_at: datetime

    class Config:
        from_attributes = True
