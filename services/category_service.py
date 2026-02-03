from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from models.category import Category
from schema.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, user_id: str, data: CategoryCreate) -> Category:
    category = Category(
        id=uuid4(),
        user_id=user_id,
        name=data.name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session, user_id: str):
    return db.query(Category).filter(
        Category.user_id == user_id,
    ).all()


def get_category(db: Session, user_id: str, category_id: str):
    return db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id,
    ).first()


def update_category(db: Session, user_id: str, category_id: str, data: CategoryUpdate):
    category = get_category(db, user_id, category_id)
    if not category:
        return None
    category.name = data.name
    category.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, user_id: str, category_id: str):
    category = get_category(db, user_id, category_id)
    if not category:
        return None
    db.delete(category)
    db.commit()
    return category

