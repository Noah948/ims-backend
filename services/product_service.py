from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.product import Product
from models.category import Category
from schema.product import ProductCreate, ProductUpdate


# CREATE
def create_product(db: Session, user_id, data: ProductCreate):
    # Ensure category belongs to user
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

    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# DELETE (HARD DELETE)
def delete_product(db: Session, user_id, product_id):
    product = get_product(db, user_id, product_id)
    db.delete(product)
    db.commit()
