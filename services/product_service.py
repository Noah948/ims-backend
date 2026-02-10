from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.product import Product
from models.category import Category
from models.user_model import User
from schema.product import ProductCreate, ProductUpdate
from utils.stock import stock_state



# CREATE

def create_product(db: Session, user_id, data: ProductCreate):
    category = db.query(Category).filter(
        Category.id == data.category_id,
        Category.user_id == user_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    product = Product(
        user_id=user_id,
        category_id=data.category_id,
        name=data.name,
        price=data.price,
        stock=data.stock,
        minimum_stock=data.minimum_stock,
        dynamic_fields=data.dynamic_fields,
    )

    user = db.query(User).filter(User.id == user_id).first()

    # total inventory quantity
    user.total_products += data.stock

    # stock state handling
    state = stock_state(data.stock, data.minimum_stock)
    if state == "low":
        user.low_stock_count += 1
    elif state == "out":
        user.out_of_stock_count += 1

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# GET ALL

def get_products(db: Session, user_id):
    return (
        db.query(Product)
        .filter(Product.user_id == user_id)
        .all()
    )


# GET ONE

def get_product(db: Session, user_id, product_id):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.user_id == user_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# UPDATE

def update_product(db: Session, user_id, product_id, data: ProductUpdate):
    product = get_product(db, user_id, product_id)
    user = db.query(User).filter(User.id == user_id).first()

    # old values
    old_stock = product.stock
    old_min = product.minimum_stock
    old_state = stock_state(old_stock, old_min)

    # apply updates
    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    # new values
    new_stock = product.stock
    new_min = product.minimum_stock
    new_state = stock_state(new_stock, new_min)

    # update total quantity
    user.total_products += (new_stock - old_stock)

    # handle state transition
    if old_state != new_state:
        if old_state == "low":
            user.low_stock_count -= 1
        elif old_state == "out":
            user.out_of_stock_count -= 1

        if new_state == "low":
            user.low_stock_count += 1
        elif new_state == "out":
            user.out_of_stock_count += 1

    db.commit()
    db.refresh(product)
    return product


# DELETE

def delete_product(db: Session, user_id, product_id):
    product = get_product(db, user_id, product_id)
    user = db.query(User).filter(User.id == user_id).first()

    # subtract quantity
    user.total_products -= product.stock

    # remove stock state
    state = stock_state(product.stock, product.minimum_stock)
    if state == "low":
        user.low_stock_count -= 1
    elif state == "out":
        user.out_of_stock -= 1

    db.delete(product)
    db.commit()
