from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, get_current_business
from models.user_model import User
from models.business import Business

from schema.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryFieldCreate,
    CategoryFieldUpdate,
    CategoryFieldResponse,
    CategoryFieldReorder,
)

from controllers.category_controller import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category,
    add_field,
    update_field,
    delete_field,
    reorder_fields,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return create_category(db, str(business.id), data)


@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_categories(db, str(business.id))


@router.get("/{category_id}", response_model=CategoryResponse)
def retrieve_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_category(db, str(business.id), str(category_id))


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return update_category(db, str(business.id), str(category_id), data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return delete_category(db, str(business.id), str(category_id))


@router.post("/{category_id}/fields", response_model=CategoryFieldResponse, status_code=status.HTTP_201_CREATED)
def add_field_endpoint(
    category_id: UUID,
    data: CategoryFieldCreate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return add_field(db, str(business.id), str(category_id), data)


@router.patch("/{category_id}/fields/reorder", response_model=List[CategoryFieldResponse])
def reorder_fields_endpoint(
    category_id: UUID,
    payload: CategoryFieldReorder,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return reorder_fields(db, str(business.id), str(category_id), payload)


@router.patch("/{category_id}/fields/{field_id}", response_model=CategoryFieldResponse)
def update_field_endpoint(
    category_id: UUID,
    field_id: UUID,
    data: CategoryFieldUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return update_field(db, str(business.id), str(category_id), str(field_id), data)


@router.delete("/{category_id}/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field_endpoint(
    category_id: UUID,
    field_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return delete_field(db, str(business.id), str(category_id), str(field_id))