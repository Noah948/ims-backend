from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
from sqlalchemy.sql import func

from models.category import Category
from models.product import Product
from models.user_model import User
from schema.category import CategoryCreate, CategoryUpdate
from utils.category_del_inventory import get_category_stock_impact

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
    category.name = data.name  # type: ignore
    category.updated_at = datetime.utcnow()  # type: ignore
    db.commit()
    db.refresh(category)
    return category


def delete_category(db, category_id: str, user_id: str):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()

    if not category:
        return None

    user = db.query(User).filter(User.id == user_id).first()

    try:
        # ----------------------------
        # 1️⃣ Calculate aggregate impact
        # ----------------------------
        total_stock, out_count, low_count = get_category_stock_impact(
            db, category_id, user_id
        )

        # ----------------------------
        # 2️⃣ Atomic user update
        # ----------------------------
        db.query(User).filter(User.id == user_id).update({
            User.total_products: User.total_products - total_stock,
            User.out_of_stock_count: User.out_of_stock_count - out_count,
            User.low_stock_count: User.low_stock_count - low_count,
        })

        # ----------------------------
        # 3️⃣ Bulk soft delete products
        # ----------------------------
        db.query(Product).filter(
            Product.category_id == category_id,
            Product.user_id == user_id
        ).update({
            Product.deleted_at: datetime.utcnow(),
            Product.category_id: None
        }, synchronize_session=False)

        # ----------------------------
        # 4️⃣ Delete category
        # ----------------------------
        db.delete(category)

        db.commit()
        return True

    except Exception:
        db.rollback()
        raise
