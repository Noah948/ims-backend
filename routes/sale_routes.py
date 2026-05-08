from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.sale import SaleCreate, SaleResponse, SaleItemReturn
from services.sale_service import (
    create_sale,
    get_sales,
    get_sale,
    # delete_sale,
    return_sale_item
)
from schema.common import PaginatedResponse

router = APIRouter(prefix="/sales", tags=["Sales"])


# ---------------- CREATE ----------------
@router.post(
    "/",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_sale_endpoint(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale, error = create_sale(
        db=db,
        user_id=current_user.id,
        data=data
    )

    if error == "PRODUCT_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Product not found")

    if error == "INSUFFICIENT_STOCK":
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock to complete sale"
        )

    return sale

# ---------------- RETURN SALE ITEM ----------------
@router.post(
    "/items/{sale_item_id}/return"
)
def return_sale_item_endpoint(
    sale_item_id: UUID,
    data: SaleItemReturn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    sale_item, error = return_sale_item(
        db=db,
        user_id=current_user.id,
        sale_item_id=sale_item_id,
        quantity=data.quantity
    )

    if error == "SALE_ITEM_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Sale item not found"
        )

    if error == "INVALID_RETURN_QUANTITY":
        raise HTTPException(
            status_code=400,
            detail="Invalid return quantity"
        )

    return {"message": "Sale item returned successfully"}


# ---------------- READ ALL ----------------
@router.get(
    "/",
    response_model=PaginatedResponse[SaleResponse]
)
def list_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_sales(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit
    )


# ---------------- READ SINGLE ----------------
@router.get(
    "/{sale_id}",
    response_model=SaleResponse
)
def retrieve_sale(
    sale_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = get_sale(
        db=db,
        user_id=current_user.id,
        sale_id=sale_id
    )

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    return sale


# ---------------- DELETE ----------------
# @router.delete(
#     "/{sale_id}",
#     status_code=status.HTTP_204_NO_CONTENT
# )
# def delete_sale_endpoint(
#     sale_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     sale = delete_sale(
#         db=db,
#         user_id=current_user.id,
#         sale_id=sale_id
#     )

#     if not sale:
#         raise HTTPException(status_code=404, detail="Sale not found")

#     return
