from fastapi import HTTPException
from sqlalchemy.orm import Session

from services.category_service import (
    create_category as create_category_service,
    get_categories as get_categories_service,
    get_category as get_category_service,
    update_category as update_category_service,
    delete_category as delete_category_service,
    add_category_field,
    update_category_field,
    delete_category_field,
    reorder_category_fields,
)
from schema.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryFieldCreate,
    CategoryFieldUpdate,
    CategoryFieldReorder,
)


def create_category(db: Session, business_id: str, data: CategoryCreate):
    return create_category_service(db, business_id, data)


def get_categories(db: Session, business_id: str):
    return get_categories_service(db, business_id)


def get_category(db: Session, business_id: str, category_id: str):
    category = get_category_service(db, business_id, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def update_category(db: Session, business_id: str, category_id: str, data: CategoryUpdate):
    category = update_category_service(db, business_id, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def delete_category(db: Session, business_id: str, category_id: str):
    deleted = delete_category_service(db, category_id, business_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return None


def add_field(db: Session, business_id: str, category_id: str, data: CategoryFieldCreate):
    try:
        field = add_category_field(db, business_id, category_id, data)
        if not field:
            raise HTTPException(status_code=404, detail="Category not found")
        return field
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def update_field(db: Session, business_id: str, category_id: str, field_id: str, data: CategoryFieldUpdate):
    try:
        field = update_category_field(db, business_id, category_id, field_id, data)
        if not field:
            raise HTTPException(status_code=404, detail="Field or category not found")
        return field
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def delete_field(db: Session, business_id: str, category_id: str, field_id: str):
    deleted = delete_category_field(db, business_id, category_id, field_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Field or category not found")
    return None


def reorder_fields(db: Session, business_id: str, category_id: str, payload: CategoryFieldReorder):
    try:
        fields = reorder_category_fields(db, business_id, category_id, payload.ordered_field_ids)
        if fields is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return fields
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))