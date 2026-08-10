from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from services.sale_service import (
    create_sale as create_sale_service,
    get_sales as get_sales_service,
    get_sale as get_sale_service,
    return_sale_item as return_sale_item_service,
)
from schema.sale import SaleCreate, SaleItemReturn


def create_sale(db: Session, business_id: UUID, user_id: UUID, data: SaleCreate):
    sale, error = create_sale_service(db, business_id, user_id, data)
    if error == "PRODUCT_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Product not found")
    if error == "INSUFFICIENT_STOCK":
        raise HTTPException(status_code=400, detail="Insufficient stock to complete sale")
    return sale


def get_sales(db: Session, business_id: UUID, page: int, limit: int):
    return get_sales_service(db, business_id, page, limit)


def get_sale(db: Session, business_id: UUID, sale_id: UUID):
    sale = get_sale_service(db, business_id, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


def return_sale_item(db: Session, business_id: UUID, user_id: UUID, sale_item_id: UUID, data: SaleItemReturn):
    sale_item, error = return_sale_item_service(
        db, business_id, user_id, sale_item_id, data.quantity
    )
    if error == "SALE_ITEM_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Sale item not found")
    if error == "INVALID_RETURN_QUANTITY":
        raise HTTPException(status_code=400, detail="Invalid return quantity")
    return {"message": "Sale item returned successfully"}