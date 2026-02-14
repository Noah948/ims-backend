from sqlalchemy.orm import Session
from uuid import uuid4

from models.category import Category
from models.product import Product
from models.user_model import User
from schema.category import CategoryCreate, CategoryUpdate
from utils.category_del_inventory import get_category_stock_impact
from sqlalchemy import func


# ---------------- CREATE ----------------
def create_category(db: Session, user_id: str, data: CategoryCreate) -> Category:
    category = Category(
        id=uuid4(),
        user_id=user_id,
        name=data.name,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ---------------- READ ALL ----------------
def get_categories(db: Session, user_id: str):
    return db.query(Category).filter(
        Category.user_id == user_id,
    ).all()


# ---------------- READ SINGLE ----------------
def get_category(db: Session, user_id: str, category_id: str):
    return db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id,
    ).first()


# ---------------- UPDATE (PATCH SAFE) ----------------
def update_category(db: Session, user_id: str, category_id: str, data: CategoryUpdate):
    category = get_category(db, user_id, category_id)
    if not category:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


# ---------------- DELETE (ATOMIC + SAFE) ----------------
def delete_category(db: Session, category_id: str, user_id: str):

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()

    if not category:
        return None

    try:
        with db.begin():

            # 1️⃣ Calculate aggregate impact
            impact = get_category_stock_impact(db, category_id, user_id)
            if impact is None:
                impact = (0, 0, 0)
            total_stock, out_count, low_count = impact

            # 2️⃣ Atomic user update
            db.query(User).filter(User.id == user_id).update({
                User.total_products: User.total_products - total_stock,
                User.out_of_stock_count: User.out_of_stock_count - out_count,
                User.low_stock_count: User.low_stock_count - low_count,
            })

            # 3️⃣ Bulk soft delete products
            db.query(Product).filter(
                Product.category_id == category_id,
                Product.user_id == user_id
            ).update({
                Product.deleted_at: func.now(),
                Product.category_id: None
            }, synchronize_session=False)

            # 4️⃣ Delete category
            db.delete(category)

        return True

    except Exception:
        db.rollback()
        raise
