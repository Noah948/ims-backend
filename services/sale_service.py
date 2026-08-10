from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
from uuid import UUID

from models.sale import Sale
from models.sale_item import SaleItem
from models.product import Product
from models.business import Business
from schema.sale import SaleCreate
from utils.inventory import apply_stock_change
from utils.pagination import paginate


def create_sale(db: Session, business_id: UUID, user_id: UUID, data: SaleCreate):
    try:
        business_stmt = select(Business).where(Business.id == business_id)
        business = db.execute(business_stmt).scalar_one()

        sale = Sale(
            business_id=business_id,
            created_by=user_id,
            contact=data.contact,
            total_amount=Decimal("0.00"),
            total_profit=Decimal("0.00")
        )
        db.add(sale)

        total_amount = Decimal("0.00")
        total_profit = Decimal("0.00")

        for item in data.items:
            stmt = (
                select(Product)
                .where(Product.id == item.product_id)
                .where(Product.business_id == business_id)
                .with_for_update()
            )
            product = db.execute(stmt).scalar_one_or_none()

            if not product:
                db.rollback()
                return None, "PRODUCT_NOT_FOUND"

            if int(product.stock) < int(item.quantity):
                db.rollback()
                return None, "INSUFFICIENT_STOCK"

            apply_stock_change(
                business=business,
                product=product,
                quantity_delta=-item.quantity
            )

            cost_price = Decimal(str(product.price))
            item_total_selling = Decimal(item.quantity) * item.selling_price
            item_total_cost = Decimal(item.quantity) * cost_price
            profit_loss = item_total_selling - item_total_cost

            sale_item = SaleItem(
                sale=sale,
                product_id=product.id,
                quantity=item.quantity,
                selling_price=item.selling_price,
                cost_price=cost_price,
                profit_loss=profit_loss
            )
            db.add(sale_item)

            total_amount += item_total_selling
            total_profit += profit_loss

        sale.total_amount = total_amount
        sale.total_profit = total_profit

        db.commit()
        db.refresh(sale)
        return sale, None

    except Exception:
        db.rollback()
        raise


def get_sales(db: Session, business_id: UUID, page: int = 1, limit: int = 10):
    query = (
        select(Sale)
        .where(Sale.business_id == business_id)
        .order_by(Sale.created_at.desc())
    )
    return paginate(query, db, page, limit)


def get_sale(db: Session, business_id: UUID, sale_id: UUID):
    stmt = (
        select(Sale)
        .where(Sale.id == sale_id)
        .where(Sale.business_id == business_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def return_sale_item(
    db: Session,
    business_id: UUID,
    user_id: UUID,
    sale_item_id: UUID,
    quantity: int
):
    try:
        stmt = (
            select(SaleItem)
            .join(Sale)
            .where(SaleItem.id == sale_item_id)
            .where(Sale.business_id == business_id)
        )
        sale_item = db.execute(stmt).scalar_one_or_none()

        if not sale_item:
            return None, "SALE_ITEM_NOT_FOUND"

        remaining_quantity = sale_item.quantity - sale_item.returned_quantity
        if quantity > remaining_quantity:
            return None, "INVALID_RETURN_QUANTITY"

        product_stmt = (
            select(Product)
            .where(Product.id == sale_item.product_id)
            .with_for_update()
        )
        product = db.execute(product_stmt).scalar_one()

        business_stmt = select(Business).where(Business.id == business_id)
        business = db.execute(business_stmt).scalar_one()

        apply_stock_change(
            business=business,
            product=product,
            quantity_delta=quantity
        )

        sale_item.returned_quantity += quantity
        if sale_item.returned_quantity == sale_item.quantity:
            sale_item.is_fully_returned = True

        db.flush()

        active_quantity = sale_item.quantity - sale_item.returned_quantity
        sale = sale_item.sale

        total_amount = Decimal("0.00")
        total_profit = Decimal("0.00")

        for item in sale.items:
            active_qty = item.quantity - item.returned_quantity
            if active_qty <= 0:
                continue
            item_total = Decimal(active_qty) * item.selling_price
            item_profit = (item.selling_price - item.cost_price) * Decimal(active_qty)
            total_amount += item_total
            total_profit += item_profit

        sale.total_amount = total_amount
        sale.total_profit = total_profit

        db.commit()
        db.refresh(sale_item)
        return sale_item, None

    except Exception:
        db.rollback()
        raise