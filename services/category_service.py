from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List

from models.category import Category
from models.product import Product
from models.user_model import User

from schema.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryFieldCreate,
    CategoryFieldUpdate
)

from utils.category_del_inventory import get_category_stock_impact


# =========================================================
# CREATE CATEGORY
# =========================================================
def create_category(
    db: Session,
    user_id: str,
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
        user_id=user_id,
        name=data.name,
        fields=fields
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


# =========================================================
# GET ALL CATEGORIES
# =========================================================
def get_categories(
    db: Session,
    user_id: str
):

    categories = db.query(Category).filter(
        Category.user_id == user_id
    ).all()

    for category in categories:
        if category.fields:
            category.fields = sorted(
                category.fields,
                key=lambda x: x.get("order", 0)
            )

    return categories


# =========================================================
# GET SINGLE CATEGORY
# =========================================================
def get_category(
    db: Session,
    user_id: str,
    category_id: str
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()

    if category and category.fields:
        category.fields = sorted(
            category.fields,
            key=lambda x: x.get("order", 0)
        )

    return category


# =========================================================
# UPDATE CATEGORY
# =========================================================
def update_category(
    db: Session,
    user_id: str,
    category_id: str,
    data: CategoryUpdate
):

    category = get_category(db, user_id, category_id)

    if not category:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        category.name = update_data["name"]

    db.commit()
    db.refresh(category)

    return category


# =========================================================
# ADD CATEGORY FIELD
# =========================================================
def add_category_field(
    db: Session,
    user_id: str,
    category_id: str,
    data: CategoryFieldCreate
):

    category = get_category(db, user_id, category_id)

    if not category:
        return None

    if not category.fields:
        category.fields = []

    # Prevent duplicate key
    if any(f["key"] == data.key for f in category.fields):
        raise ValueError(
            f"Field with key '{data.key}' already exists"
        )

    new_field = {
        "id": str(uuid4()),
        "key": data.key,
        "type": data.type,
        "required": getattr(data, "required", False),
        "order": len(category.fields) + 1,
        "meta": getattr(data, "meta", {})
    }

    category.fields.append(new_field)

    db.commit()
    db.refresh(category)

    return new_field


# =========================================================
# UPDATE CATEGORY FIELD
# =========================================================
def update_category_field(
    db: Session,
    user_id: str,
    category_id: str,
    field_id: str,
    data: CategoryFieldUpdate
):

    category = get_category(db, user_id, category_id)

    if not category or not category.fields:
        return None

    updates = data.model_dump(exclude_unset=True)

    new_fields = []
    updated_field = None

    for field in category.fields:

        if field["id"] == field_id:

            updates.pop("id", None)

            # Prevent duplicate key
            if "key" in updates:
                if any(
                    f["key"] == updates["key"]
                    and f["id"] != field_id
                    for f in category.fields
                ):
                    raise ValueError(
                        f"Field with key '{updates['key']}' already exists"
                    )

            updated_field = {
                **field,
                **updates
            }

            new_fields.append(updated_field)

        else:
            new_fields.append(field)

    if not updated_field:
        return None

    category.fields = new_fields

    db.commit()
    db.refresh(category)

    return updated_field


# =========================================================
# DELETE CATEGORY FIELD
# =========================================================
def delete_category_field(
    db: Session,
    user_id: str,
    category_id: str,
    field_id: str
):

    category = get_category(db, user_id, category_id)

    if not category or not category.fields:
        return False

    new_fields = [
        field for field in category.fields
        if field["id"] != field_id
    ]

    # Normalize order
    for index, field in enumerate(new_fields, start=1):
        field["order"] = index

    category.fields = new_fields

    db.commit()
    db.refresh(category)

    return True


# =========================================================
# REORDER CATEGORY FIELDS
# =========================================================
def reorder_category_fields(
    db: Session,
    user_id: str,
    category_id: str,
    ordered_field_ids: List[str]
):

    category = get_category(db, user_id, category_id)

    if not category or not category.fields:
        return None

    existing_fields = {
        field["id"]: field
        for field in category.fields
    }

    # Validate IDs
    if set(ordered_field_ids) != set(existing_fields.keys()):
        raise ValueError("Field IDs mismatch")

    new_fields = []

    # Assign fresh order
    for index, field_id in enumerate(ordered_field_ids, start=1):

        field = existing_fields[field_id]

        updated_field = {
            **field,
            "order": index
        }

        new_fields.append(updated_field)

    category.fields = new_fields

    db.commit()
    db.refresh(category)

    return category.fields


# =========================================================
# DELETE CATEGORY
# =========================================================
def delete_category(
    db: Session,
    category_id: str,
    user_id: str
):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()

    if not category:
        return None

    try:

        impact = get_category_stock_impact(
            db,
            category_id,
            user_id
        )

        if impact is None:
            impact = (0, 0, 0)

        total_stock, out_count, low_count = impact

        db.query(User).filter(
            User.id == user_id
        ).update({
            User.total_products:
                User.total_products - total_stock,

            User.out_of_stock_count:
                User.out_of_stock_count - out_count,

            User.low_stock_count:
                User.low_stock_count - low_count,
        })

        db.query(Product).filter(
            Product.category_id == category_id,
            Product.user_id == user_id
        ).delete(synchronize_session=False)

        db.delete(category)

        db.commit()

        return True

    except Exception:
        db.rollback()
        raise