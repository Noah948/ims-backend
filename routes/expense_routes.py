from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_business

from models.business import Business

from schema.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseFilter,
)

from services.expense_service import (
    create_expense,
    get_expenses,
    get_expense,
    update_expense,
    delete_expense,
    get_expenses_with_filters,
)


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_endpoint(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return create_expense(
        db,
        business.id,
        data,
    )


@router.get(
    "/",
    response_model=List[ExpenseResponse],
)
def list_expenses(
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_expenses(
        db,
        business.id,
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def retrieve_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_expense(
        db,
        business.id,
        expense_id,
    )


@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
)
def update_expense_endpoint(
    expense_id: UUID,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return update_expense(
        db,
        business.id,
        expense_id,
        data,
    )


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense_endpoint(
    expense_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    delete_expense(
        db,
        business.id,
        expense_id,
    )

    return None


@router.post(
    "/filter",
    response_model=List[ExpenseResponse],
)
def filter_expenses_endpoint(
    filters: ExpenseFilter,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_expenses_with_filters(
        db,
        business.id,
        filters,
    )