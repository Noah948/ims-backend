from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.sale import SaleCreate, SaleResponse
from services.sale_service import (
    create_sale,
    get_sales,
    get_sale,
    delete_sale
)

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
    sale, error = create_sale(db=db, user_id=str(current_user.id), data=data)

    if error == "PRODUCT_NOT_FOUND":
        raise HTTPException(status_code=404, detail="Product not found")

    if error == "INSUFFICIENT_STOCK":
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock to complete sale"
        )

    return sale


# ---------------- READ ALL ----------------
@router.get(
    "/",
    response_model=List[SaleResponse]
)
def list_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_sales(db=db, user_id=str(current_user.id))


# ---------------- READ SINGLE ----------------
@router.get(
    "/{sale_id}",
    response_model=SaleResponse
)
def retrieve_sale(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = get_sale(db=db, user_id=str(current_user.id), sale_id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


# ---------------- DELETE (RETURN PRODUCT) ----------------
@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_sale_endpoint(
    sale_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sale = delete_sale(db=db, user_id=str(current_user.id), sale_id=sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return
