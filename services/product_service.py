from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.product import Product
from models.category import Category
from models.business import Business
from schema.product import ProductCreate, ProductUpdate
from utils.inventory import apply_stock_change
from sqlalchemy import select
from utils.pagination import paginate
from scheduler.policies import PRODUCT_RETENTION_DAYS


def validate_dynamic_fields(category: Category, product_fields: dict):
    if not category.fields:
        if product_fields:
            raise HTTPException(status_code=400, detail="This category does not allow dynamic fields")
        return
    allowed_fields = {field["key"]: field for field in category.fields}
    for key in product_fields.keys():
        if key not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"Field '{key}' is not allowed for this category")
    for key, value in product_fields.items():
        expected_type = allowed_fields[key]["type"]
        if expected_type == "string" and not isinstance(value, str):
            raise HTTPException(status_code=400, detail=f"{key} must be string")
        if expected_type == "number" and not isinstance(value, (int, float)):
            raise HTTPException(status_code=400, detail=f"{key} must be number")
        if expected_type == "date" and not isinstance(value, str):
            raise HTTPException(status_code=400, detail=f"{key} must be date string")


def create_product(db: Session, business_id, data: ProductCreate):
    category = None
    if data.category_id:
        category = db.query(Category).filter(
            Category.id == data.category_id,
            Category.business_id == business_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    if category:
        validate_dynamic_fields(category, data.dynamic_fields or {})

    business = db.query(Business).filter(Business.id == business_id).first()

    product = Product(
        business_id=business_id,
        category_id=data.category_id,
        name=data.name,
        price=data.price,
        stock=0,
        minimum_stock=data.minimum_stock,
        dynamic_fields=data.dynamic_fields,
    )
    db.add(product)
    db.flush()

    if data.stock:
        apply_stock_change(
            business=business,
            product=product,
            quantity_delta=data.stock,
            is_new=True,
        )

    db.commit()
    db.refresh(product)
    return product


def get_products(db: Session, business_id, page: int = 1, limit: int = 10):
    query = (
        select(Product)
        .where(Product.business_id == business_id, Product.deleted_at.is_(None))
        .order_by(Product.created_at.desc())
    )
    return paginate(query, db, page, limit)


def get_product(db: Session, business_id, product_id):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.business_id == business_id,
        Product.deleted_at.is_(None)
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def update_product(db: Session, business_id, product_id, data: ProductUpdate):
    product = get_product(db, business_id, product_id)
    business = db.query(Business).filter(Business.id == business_id).first()
    update_data = data.model_dump(exclude_unset=True)
    quantity_delta = 0
    new_minimum_stock = None

    if "stock" in update_data:
        new_stock = update_data.pop("stock")
        quantity_delta = new_stock - product.stock

    if "minimum_stock" in update_data:
        new_minimum_stock = update_data.pop("minimum_stock")

    category = None
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"],
            Category.business_id == business_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    else:
        category = product.category

    if "dynamic_fields" in update_data:
        validate_dynamic_fields(category, update_data["dynamic_fields"] or {})

    if quantity_delta != 0 or new_minimum_stock is not None:
        apply_stock_change(
            business=business,
            product=product,
            quantity_delta=quantity_delta,
            new_minimum_stock=new_minimum_stock,
        )

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, business_id, product_id):
    product = get_product(db, business_id, product_id)
    business = db.query(Business).filter(Business.id == business_id).first()
    apply_stock_change(business=business, product=product, is_delete=True)
    product.deleted_at = datetime.now(UTC)
    db.commit()
    return None


def add_product_quantity(db: Session, business_id, product_id, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    product = get_product(db, business_id, product_id)
    business = db.query(Business).filter(Business.id == business_id).first()
    apply_stock_change(business=business, product=product, quantity_delta=quantity)
    db.commit()
    db.refresh(product)
    return product


def decrease_product_quantity(db: Session, business_id, product_id, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    product = get_product(db, business_id, product_id)
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
    business = db.query(Business).filter(Business.id == business_id).first()
    apply_stock_change(business=business, product=product, quantity_delta=-quantity)
    db.commit()
    db.refresh(product)
    return product


def cleanup_deleted_products(db: Session):
    cutoff = datetime.now(UTC) - timedelta(days=PRODUCT_RETENTION_DAYS)
    (
        db.query(Product)
        .filter(Product.deleted_at.isnot(None), Product.deleted_at < cutoff)
        .delete(synchronize_session=False)
    )
    db.commit()