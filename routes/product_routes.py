from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Sequence
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


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    return create_product(db, current_user.id, data)


@router.get("/", response_model=List[ProductResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Sequence[ProductResponse]:
    return get_products(db, current_user.id)


@router.get("/{product_id}", response_model=ProductResponse)
def get_one(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    return get_product(db, current_user.id, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    return update_product(db, current_user.id, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> None:
    delete_product(db, current_user.id, product_id)


@router.post("/{product_id}/add", response_model=ProductResponse)
def add_quantity(
    product_id: UUID,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    return add_product_quantity(
        db,
        current_user.id,
        product_id,
        payload.quantity
    )


@router.post("/{product_id}/remove", response_model=ProductResponse)
def remove_quantity(
    product_id: UUID,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProductResponse:
    return decrease_product_quantity(
        db,
        current_user.id,
        product_id,
        payload.quantity
    )
