from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from schema.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    QuantityUpdate
)
from services.product_service import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
    add_product_quantity,
    decrease_product_quantity
)

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------- CREATE ----------------
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_product(db, current_user.id, data)


# ---------------- LIST ----------------
@router.get("/", response_model=List[ProductResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_products(db, current_user.id)


# ---------------- GET ONE ----------------
@router.get("/{product_id}", response_model=ProductResponse)
def get_one(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_product(db, current_user.id, product_id)


# ---------------- UPDATE ----------------
@router.put("/{product_id}", response_model=ProductResponse)
def update(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_product(db, current_user.id, product_id, data)


# ---------------- DELETE ----------------
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    delete_product(db, current_user.id, product_id)


# ---------------- ADD STOCK ----------------
@router.post("/{product_id}/add", response_model=ProductResponse)
def add_quantity(
    product_id: UUID,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return add_product_quantity(
        db,
        current_user.id,
        product_id,
        payload.quantity
    )


# ---------------- REMOVE STOCK ----------------
@router.post("/{product_id}/remove", response_model=ProductResponse)
def remove_quantity(
    product_id: UUID,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return decrease_product_quantity(
        db,
        current_user.id,
        product_id,
        payload.quantity
    )
