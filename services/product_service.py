from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.product import Product
from models.category import Category
from models.user_model import User
from schema.product import ProductCreate, ProductUpdate
from utils.inventory import apply_stock_change
from utils.stock import stock_state


# ---------------- CREATE ----------------
def create_product(db: Session, user_id, data: ProductCreate):
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
        stock=0,
        minimum_stock=data.minimum_stock,
        dynamic_fields=data.dynamic_fields,
    )

    db.add(product)
    db.flush()

    # 🔥 Register product properly through inventory layer
    apply_stock_change(
        user=user,
        product=product,
        quantity_delta=data.stock or 0,
        is_new=True,
    )

    db.commit()
    db.refresh(product)
    return product



# ---------------- GET ALL ----------------
def get_products(db: Session, user_id):
    return db.query(Product).filter(Product.user_id == user_id).all()


# ---------------- GET ONE ----------------
def get_product(db: Session, user_id, product_id):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == user_id
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

    update_data = data.dict(exclude_unset=True)

    quantity_delta = 0
    new_minimum_stock = None

    # Extract stock change
    if "stock" in update_data:
        new_stock = update_data.pop("stock")
        quantity_delta = new_stock - product.stock

    # Extract minimum_stock change
    if "minimum_stock" in update_data:
        new_minimum_stock = update_data.pop("minimum_stock")

    # 🔥 Let inventory engine handle stock + state logic
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


# ---------------- DELETE ----------------
def delete_product(db: Session, user_id, product_id):
    product = get_product(db, user_id, product_id)
    user = db.query(User).filter(User.id == user_id).first()

    # 🔥 Let inventory engine handle everything
    apply_stock_change(
        user=user,
        product=product,
        is_delete=True,
    )

    db.delete(product)
    db.commit()


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
    user = db.query(User).filter(User.id == user_id).first()

    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    apply_stock_change(
        user=user,
        product=product,
        quantity_delta=-quantity
    )

    db.commit()
    db.refresh(product)
    return product
