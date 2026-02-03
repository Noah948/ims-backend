from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from models.category_field import CategoryField
from models.category import Category
from schema.category_field import CategoryFieldCreate, CategoryFieldUpdate


def create_category_field(db: Session, category_id: str, data: CategoryFieldCreate, user_id: str):
    # Check if category belongs to user
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()
    if not category:
        return None

    field = CategoryField(
        id=uuid4(),
        category_id=category_id,
        field_name=data.field_name,
        field_type=data.field_type,
        dropdown_options=data.dropdown_options,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(field)
    db.commit()
    db.refresh(field)
    return field


def get_category_fields(db: Session, category_id: str, user_id: str):
    # Ensure category belongs to user
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()
    if not category:
        return []

    return db.query(CategoryField).filter(
        CategoryField.category_id == category_id
    ).all()


def get_category_field(db: Session, category_id: str, field_id: str, user_id: str):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()
    if not category:
        return None

    return db.query(CategoryField).filter(
        CategoryField.id == field_id,
        CategoryField.category_id == category_id
    ).first()


def update_category_field(db: Session, category_id: str, field_id: str, data: CategoryFieldUpdate, user_id: str):
    field = get_category_field(db, category_id, field_id, user_id)
    if not field:
        return None

    if data.field_name is not None:
        field.field_name = data.field_name
    if data.field_type is not None:
        field.field_type = data.field_type
    if data.dropdown_options is not None:
        field.dropdown_options = data.dropdown_options

    field.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(field)
    return field


def delete_category_field(db: Session, category_id: str, field_id: str, user_id: str):
    field = get_category_field(db, category_id, field_id, user_id)
    if not field:
        return None

    db.delete(field)
    db.commit()
    return field
