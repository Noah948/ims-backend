from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4, UUID

from models.category_field import CategoryField
from models.category import Category
from schema.category_field import CategoryFieldCreate, CategoryFieldUpdate


# -----------------------------------------------------
# Internal helper (avoid repeating ownership check)
# -----------------------------------------------------
def _get_user_category(db: Session, category_id: UUID, user_id: UUID):
    return db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()


# -----------------------------------------------------
# Create
# -----------------------------------------------------
def create_category_field(
    db: Session,
    category_id: UUID,
    data: CategoryFieldCreate,
    user_id: UUID
):
    category = _get_user_category(db, category_id, user_id)
    if not category:
        return None

    field = CategoryField(
        id=uuid4(),
        category_id=category_id,
        field_name=data.field_name,
        field_type=data.field_type,
        dropdown_options=data.dropdown_options,
    )

    try:
        db.add(field)
        db.commit()
        db.refresh(field)
        return field
    except SQLAlchemyError:
        db.rollback()
        raise


# -----------------------------------------------------
# List
# -----------------------------------------------------
def get_category_fields(db: Session, category_id: UUID, user_id: UUID):
    category = _get_user_category(db, category_id, user_id)
    if not category:
        return []

    return db.query(CategoryField).filter(
        CategoryField.category_id == category_id
    ).all()


# -----------------------------------------------------
# Get single
# -----------------------------------------------------
def get_category_field(
    db: Session,
    category_id: UUID,
    field_id: UUID,
    user_id: UUID
):
    category = _get_user_category(db, category_id, user_id)
    if not category:
        return None

    return db.query(CategoryField).filter(
        CategoryField.id == field_id,
        CategoryField.category_id == category_id
    ).first()


# -----------------------------------------------------
# Update
# -----------------------------------------------------
def update_category_field(
    db: Session,
    category_id: UUID,
    field_id: UUID,
    data: CategoryFieldUpdate,
    user_id: UUID
):
    field = get_category_field(db, category_id, field_id, user_id)
    if not field:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Handle type change safely
    if "field_type" in update_data:
        field.field_type = update_data["field_type"]

        # If changed to non-dropdown → remove options
        if update_data["field_type"] != "dropdown":
            field.dropdown_options = None

    if "field_name" in update_data:
        field.field_name = update_data["field_name"]

    if "dropdown_options" in update_data:
        field.dropdown_options = update_data["dropdown_options"]

    try:
        db.commit()
        db.refresh(field)
        return field
    except SQLAlchemyError:
        db.rollback()
        raise


# -----------------------------------------------------
# Delete
# -----------------------------------------------------
def delete_category_field(
    db: Session,
    category_id: UUID,
    field_id: UUID,
    user_id: UUID
):
    field = get_category_field(db, category_id, field_id, user_id)
    if not field:
        return None

    try:
        db.delete(field)
        db.commit()
        return field
    except SQLAlchemyError:
        db.rollback()
        raise
