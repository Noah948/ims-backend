from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List
from datetime import datetime, timedelta, UTC

from scheduler.policies import CATEGORY_RETENTION_DAYS

from models.category import Category
from models.product import Product

from schema.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryFieldCreate,
    CategoryFieldUpdate,
)

from utils.category_del_inventory import get_category_stock_impact


def normalize_fields(fields):
    if not fields:
        return []

    normalized = []

    for index, field in enumerate(fields, start=1):
        normalized.append({
            **field,
            "meta": field.get("meta") or {},
            "required": field.get("required", False),
            "order": field.get("order", index),
        })

    return sorted(normalized, key=lambda x: x["order"])


def create_category(
    db: Session,
    business_id: str,
    data: CategoryCreate
) -> Category:
    fields = []

    if data.fields:
        for index, field in enumerate(data.fields, start=1):
            field_dict = field.model_dump()
            field_dict["id"] = str(uuid4())
            field_dict["order"] = index
            fields.append(field_dict)

    category = Category(
        id=uuid4(),
        business_id=business_id,
        name=data.name,
        fields=fields
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_categories(
    db: Session,
    business_id: str
):
    categories = db.query(Category).filter(
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).all()

    for category in categories:
        category.fields = normalize_fields(category.fields)

    return categories


def get_category(
    db: Session,
    business_id: str,
    category_id: str
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category.fields:
        category.fields = normalize_fields(category.fields)

    return category


def update_category(
    db: Session,
    business_id: str,
    category_id: str,
    data: CategoryUpdate
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        category.name = update_data["name"]

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category_id: str,
    business_id: str
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    active_product_exists = db.query(Product.id).filter(
        Product.category_id == category_id,
        Product.business_id == business_id,
        Product.deleted_at.is_(None)
    ).first()

    if active_product_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category. Delete all products in this category first."
        )

    try:
        category.deleted_at = datetime.now(UTC)

        db.commit()
        db.refresh(category)

        return True

    except Exception:
        db.rollback()
        raise


def add_category_field(
    db: Session,
    business_id: str,
    category_id: str,
    data: CategoryFieldCreate
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    fields = category.fields or []

    if any(f["key"] == data.key for f in fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field with key '{data.key}' already exists"
        )

    new_field = {
        "id": str(uuid4()),
        "key": data.key,
        "type": data.type,
        "required": getattr(data, "required", False),
        "order": len(fields) + 1,
        "meta": getattr(data, "meta", {})
    }

    category.fields = [
        *fields,
        new_field
    ]

    db.commit()
    db.refresh(category)

    return new_field


def update_category_field(
    db: Session,
    business_id: str,
    category_id: str,
    field_id: str,
    data: CategoryFieldUpdate
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category or not category.fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field or category not found"
        )

    updates = data.model_dump(exclude_unset=True)

    new_fields = []
    updated_field = None

    for field in category.fields:
        if field["id"] == field_id:
            updates.pop("id", None)

            if "key" in updates:
                if any(
                    f["key"] == updates["key"] and f["id"] != field_id
                    for f in category.fields
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field with key '{updates['key']}' already exists"
                    )

            updated_field = {
                **field,
                **updates
            }

            new_fields.append(updated_field)

        else:
            new_fields.append(field)

    if not updated_field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field or category not found"
        )

    category.fields = new_fields

    db.commit()
    db.refresh(category)

    return updated_field


def delete_category_field(
    db: Session,
    business_id: str,
    category_id: str,
    field_id: str
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category or not category.fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field or category not found"
        )

    field_exists = any(
        field["id"] == field_id
        for field in category.fields
    )

    if not field_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field or category not found"
        )

    new_fields = [
        field
        for field in category.fields
        if field["id"] != field_id
    ]

    for index, field in enumerate(new_fields, start=1):
        field["order"] = index

    category.fields = new_fields

    db.commit()
    db.refresh(category)

    return True


def reorder_category_fields(
    db: Session,
    business_id: str,
    category_id: str,
    ordered_field_ids: List[str]
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.business_id == business_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category or not category.fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    existing_fields = {
        field["id"]: field
        for field in category.fields
    }

    if set(ordered_field_ids) != set(existing_fields.keys()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field IDs mismatch"
        )

    new_fields = []

    for index, field_id in enumerate(ordered_field_ids, start=1):
        field = existing_fields[field_id]

        new_fields.append({
            **field,
            "order": index
        })

    category.fields = new_fields

    db.commit()
    db.refresh(category)

    return category.fields


def cleanup_deleted_categories(db: Session):
    cutoff = datetime.now(UTC) - timedelta(
        days=CATEGORY_RETENTION_DAYS
    )

    (
        db.query(Category)
        .filter(
            Category.deleted_at.is_not(None),
            Category.deleted_at < cutoff
        )
        .delete(synchronize_session=False)
    )

    db.commit()