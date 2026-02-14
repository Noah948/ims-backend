from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status

from models.product import Product
from models.category import Category
from models.user_model import User
from schema.product import ProductCreate, ProductUpdate
from utils.inventory import apply_stock_change


# ---------------- CREATE ----------------
def create_product(db: Session, user_id, data: ProductCreate):

    # Validate category if provided
    if data.category_id:
        category = db.query(Category).filter(
            Category.id == data.category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    user = db.query(User).filter(User.id == user_id).first()

    product = Product(
        user_id=user_id,
        category_id=data.category_id,
        name=data.name,
        price=data.price,
        stock=0,  # inventory engine will adjust
        minimum_stock=data.minimum_stock,
        dynamic_fields=data.dynamic_fields,
    )

    db.add(product)
    db.flush()

    # Register through inventory layer
    if data.stock:
        apply_stock_change(
            user=user,
            product=product,
            quantity_delta=data.stock,
            is_new=True,
        )

    db.commit()
    db.refresh(product)
    return product


# ---------------- GET ALL ----------------
def get_products(db: Session, user_id):
    return db.query(Product).filter(
        Product.user_id == user_id,
        Product.deleted_at.is_(None)
    ).all()


# ---------------- GET ONE ----------------
def get_product(db: Session, user_id, product_id):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id,
        Product.deleted_at.is_(None)
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# ---------------- UPDATE ----------------
def update_product(db: Session, user_id, product_id, data: ProductUpdate):
    product = get_product(db, user_id, product_id)
    user = db.query(User).filter(User.id == user_id).first()

    update_data = data.model_dump(exclude_unset=True)

    quantity_delta = 0
    new_minimum_stock = None

    # Handle stock change
    if "stock" in update_data:
        new_stock = update_data.pop("stock")
        quantity_delta = new_stock - product.stock

    # Handle minimum_stock change
    if "minimum_stock" in update_data:
        new_minimum_stock = update_data.pop("minimum_stock")

    # Validate category change
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"],
            Category.user_id == user_id
        ).first()

        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    # Inventory engine handles stock logic
    if quantity_delta != 0 or new_minimum_stock is not None:
        apply_stock_change(
            user=user,
            product=product,
            quantity_delta=quantity_delta,
            new_minimum_stock=new_minimum_stock,
        )

    # Update remaining fields
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# ---------------- DELETE (Soft Delete) ----------------
def delete_product(db: Session, user_id, product_id):
    product = get_product(db, user_id, product_id)
    user = db.query(User).filter(User.id == user_id).first()

    apply_stock_change(
        user=user,
        product=product,
        is_delete=True,
    )

    product.deleted_at = datetime.utcnow()
    db.commit()
    return None


# ---------------- ADD QUANTITY ----------------
def add_product_quantity(db: Session, user_id, product_id, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    product = get_product(db, user_id, product_id)
    user = db.query(User).filter(User.id == user_id).first()

    apply_stock_change(
        user=user,
        product=product,
        quantity_delta=quantity
    )

    db.commit()
    db.refresh(product)
    return product


# ---------------- REMOVE QUANTITY ----------------
def decrease_product_quantity(db: Session, user_id, product_id, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    product = get_product(db, user_id, product_id)

    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    user = db.query(User).filter(User.id == user_id).first()

    apply_stock_change(
        user=user,
        product=product,
        quantity_delta=-quantity
    )

    db.commit()
    db.refresh(product)
    return product
