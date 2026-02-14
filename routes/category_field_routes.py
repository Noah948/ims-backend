from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.category_field import (
    CategoryFieldCreate,
    CategoryFieldUpdate,
    CategoryFieldResponse
)
from services.category_field_service import (
    create_category_field,
    get_category_fields,
    get_category_field,
    update_category_field,
    delete_category_field
)

router = APIRouter(
    prefix="/categories/{category_id}/fields",
    tags=["CategoryFields"]
)


# Create
@router.post("/", response_model=CategoryFieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(
    category_id: UUID,
    data: CategoryFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = create_category_field(db, category_id, data, current_user.id)
    if not field:
        raise HTTPException(status_code=404, detail="Category not found")
    return field


# List
@router.get("/", response_model=List[CategoryFieldResponse])
def list_fields(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_category_fields(db, category_id, current_user.id)


# Get single
@router.get("/{field_id}", response_model=CategoryFieldResponse)
def get_field(
    category_id: UUID,
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = get_category_field(db, category_id, field_id, current_user.id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


# Update
@router.put("/{field_id}", response_model=CategoryFieldResponse)
@router.patch("/{field_id}", response_model=CategoryFieldResponse)
def update_field(
    category_id: UUID,
    field_id: UUID,
    data: CategoryFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = update_category_field(db, category_id, field_id, data, current_user.id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


# Delete
@router.delete("/{field_id}", response_model=CategoryFieldResponse)
def delete_field(
    category_id: UUID,
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = delete_category_field(db, category_id, field_id, current_user.id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
