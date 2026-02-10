from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4
from decimal import Decimal

from models.sale import Sale
from models.product import Product
from schema.sale import SaleCreate


# ---------------- CREATE ----------------
def create_sale(db: Session, user_id: str, data: SaleCreate):
    # Fetch product
    stmt = (
        select(Product)
        .where(Product.id == data.product_id)
        .where(Product.user_id == user_id)
    )
    product = db.execute(stmt).scalar_one_or_none()

    if not product:
        return None, "PRODUCT_NOT_FOUND"

    # ❌ Block if insufficient stock
    if int(product.stock) < int(data.quantity):
        return None, "INSUFFICIENT_STOCK"

    # Profit / Loss calculation
    total_selling = Decimal(data.quantity) * data.selling_price
    total_cost = Decimal(data.quantity) * product.price
    profit_loss = total_selling - total_cost

    # ✅ Reduce stock
    product.stock -= data.quantity

    sale = Sale(
        id=uuid4(),
        user_id=user_id,
        product_id=data.product_id,
        quantity=data.quantity,
        selling_price=data.selling_price,
        profit_loss=profit_loss,
        contact=data.contact
    )

    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale, None

# ---------------- READ ALL ----------------
def get_sales(db: Session, user_id: str):
    stmt = select(Sale).where(Sale.user_id == user_id)
    return db.execute(stmt).scalars().all()


# ---------------- READ SINGLE ----------------
def get_sale(db: Session, user_id: str, sale_id: str):
    stmt = (
        select(Sale)
        .where(Sale.id == sale_id)
        .where(Sale.user_id == user_id)
    )
    return db.execute(stmt).scalar_one_or_none()


# ---------------- DELETE (RETURN PRODUCT) ----------------
def delete_sale(db: Session, user_id: str, sale_id: str):
    stmt = (
        select(Sale)
        .where(Sale.id == sale_id)
        .where(Sale.user_id == user_id)
    )
    sale = db.execute(stmt).scalar_one_or_none()

    if not sale:
        return None

    # Fetch product
    product_stmt = (
        select(Product)
        .where(Product.id == sale.product_id)
        .where(Product.user_id == user_id)
    )
    product = db.execute(product_stmt).scalar_one_or_none()

    if product:
        # ✅ Restore stock
        product.stock += sale.quantity

    db.delete(sale)
    db.commit()
    return sale
