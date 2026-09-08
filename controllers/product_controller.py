# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# from uuid import UUID

# from services.product_service import (
#     create_product as create_product_service,
#     get_products as get_products_service,
#     get_product as get_product_service,
#     update_product as update_product_service,
#     delete_product as delete_product_service,
#     add_product_quantity,
#     decrease_product_quantity,
# )
# from schema.product import ProductCreate, ProductUpdate


# def create_product(db: Session, business_id: UUID, data: ProductCreate):
#     return create_product_service(db, business_id, data)


# def get_products(db: Session, business_id: UUID, page: int, limit: int):
#     return get_products_service(db, business_id, page, limit)


# def get_product(db: Session, business_id: UUID, product_id: UUID):
#     return get_product_service(db, business_id, product_id)


# def update_product(db: Session, business_id: UUID, product_id: UUID, data: ProductUpdate):
#     return update_product_service(db, business_id, product_id, data)


# def delete_product(db: Session, business_id: UUID, product_id: UUID):
#     delete_product_service(db, business_id, product_id)
#     return None


# def add_quantity(db: Session, business_id: UUID, product_id: UUID, quantity: int):
#     return add_product_quantity(db, business_id, product_id, quantity)


# def remove_quantity(db: Session, business_id: UUID, product_id: UUID, quantity: int):
#     return decrease_product_quantity(db, business_id, product_id, quantity)