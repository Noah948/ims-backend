from datetime import date

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from core.database import get_db
from services.seed_service import delete_seeded_business, seed_business


# Dev-only: registered in main.py only when ENABLE_SEED=true.
router = APIRouter(
    prefix="/dev",
    tags=["Dev Seed"],
)


class SeedRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    business_name: str = Field(..., min_length=1)
    start_date: date


class SeedDeleteRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_endpoint(
    data: SeedRequest,
    db: Session = Depends(get_db),
):
    return seed_business(
        db,
        data.email,
        data.password,
        data.business_name,
        data.start_date,
    )


# POST, not DELETE: Swagger UI doesn't send a request body with DELETE reliably.
@router.post("/seed/delete")
def delete_seed_endpoint(
    data: SeedDeleteRequest,
    db: Session = Depends(get_db),
):
    return delete_seeded_business(
        db,
        data.email,
        data.password,
    )
