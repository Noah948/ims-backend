from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from schema.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from services.category_service import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category
)
from models.user_model import User

router = APIRouter(prefix="/categories", tags=["Categories"])


# ---------------- CREATE ----------------
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_category(db=db, user_id=str(current_user.id), data=data)


# ---------------- READ ALL ----------------
@router.get(
    "/",
    response_model=List[CategoryResponse]
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_categories(db, user_id=str(current_user.id))


# ---------------- READ SINGLE ----------------
@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def retrieve_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = get_category(
        db,
        user_id=str(current_user.id),
        category_id=str(category_id)
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


# ---------------- UPDATE ----------------
@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
@router.patch(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category_endpoint(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = update_category(
        db=db,
        user_id=str(current_user.id),
        category_id=str(category_id),
        data=data
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


# ---------------- DELETE ----------------
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category_endpoint(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = delete_category(
        db=db,
        user_id=str(current_user.id),
        category_id=str(category_id)
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")

    return
