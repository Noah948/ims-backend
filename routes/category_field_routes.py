from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

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

router = APIRouter(prefix="/categories/{category_id}/fields", tags=["CategoryFields"])


# Create Field
@router.post("/", response_model=CategoryFieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(
    category_id: str,
    data: CategoryFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = create_category_field(db, category_id, data, str(current_user.id))
    if not field:
        raise HTTPException(status_code=404, detail="Category not found")
    return field


# List Fields
@router.get("/", response_model=List[CategoryFieldResponse])
def list_fields(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_category_fields(db, category_id, str(current_user.id))


# Get single field
@router.get("/{field_id}", response_model=CategoryFieldResponse)
def get_field(
    category_id: str,
    field_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = get_category_field(db, category_id, field_id, str(current_user.id))
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


# Update field
@router.put("/{field_id}", response_model=CategoryFieldResponse)
@router.patch("/{field_id}", response_model=CategoryFieldResponse)
def update_field(
    category_id: str,
    field_id: str,
    data: CategoryFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = update_category_field(db, category_id, field_id, data, str(current_user.id))
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


# Delete field
@router.delete("/{field_id}", response_model=CategoryFieldResponse)
def delete_field(
    category_id: str,
    field_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = delete_category_field(db, category_id, field_id, str(current_user.id))
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
