from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, get_current_business
from models.user_model import User
from models.business import Business
from schema.sale import SaleCreate, SaleResponse, SaleItemReturn
from schema.common import PaginatedResponse

from controllers.sale_controller import (
    create_sale,
    get_sales,
    get_sale,
    return_sale_item,
)

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale_endpoint(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
):
    return create_sale(db, business.id, current_user.id, data)


@router.post("/items/{sale_item_id}/return")
def return_sale_item_endpoint(
    sale_item_id: UUID,
    data: SaleItemReturn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
):
    return return_sale_item(db, business.id, current_user.id, sale_item_id, data)


@router.get("/", response_model=PaginatedResponse[SaleResponse])
def list_sales(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_sales(db, business.id, page, limit)


@router.get("/{sale_id}", response_model=SaleResponse)
def retrieve_sale(
    sale_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_sale(db, business.id, sale_id)