from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from schema.common import PaginatedResponse

from core.database import get_db
from core.dependencies import get_current_business, require_permission
from core.permissions import Permission

from models.business import Business

from schema.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    QuantityUpdate,
)

from services.product_service import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
    add_product_quantity,
    decrease_product_quantity,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.CREATE_PRODUCTS))],
)
def create(
    data: ProductCreate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return create_product(
        db,
        business.id,
        data
    )


@router.get(
    "/",
    response_model=PaginatedResponse[ProductResponse]
)
def list_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_products(
        db,
        business.id,
        page,
        limit
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_one(
    product_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_product(
        db,
        business.id,
        product_id
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission(Permission.EDIT_PRODUCTS))],
)
def update(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return update_product(
        db,
        business.id,
        product_id,
        data
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.DELETE_PRODUCTS))],
)
def delete(
    product_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return delete_product(
        db,
        business.id,
        product_id
    )


@router.post(
    "/{product_id}/add",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission(Permission.EDIT_PRODUCTS))],
)
def add_quantity_endpoint(
    product_id: UUID,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return add_product_quantity(
        db,
        business.id,
        product_id,
        payload.quantity
    )


@router.post(
    "/{product_id}/remove",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission(Permission.EDIT_PRODUCTS))],
)
def remove_quantity_endpoint(
    product_id: UUID,
    payload: QuantityUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return decrease_product_quantity(
        db,
        business.id,
        product_id,
        payload.quantity
    )