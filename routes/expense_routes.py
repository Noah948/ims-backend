from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse
)
from services.expense_service import (
    create_expense,
    get_expenses,
    get_expense,
    update_expense,
    delete_expense
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ---------------- CREATE ----------------
@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense_endpoint(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense, _ = create_expense(
        db=db,
        user_id=current_user.id,
        data=data
    )

    return expense


# ---------------- READ ALL ----------------
@router.get(
    "/",
    response_model=List[ExpenseResponse]
)
def list_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_expenses(
        db=db,
        user_id=current_user.id
    )


# ---------------- READ SINGLE ----------------
@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse
)
def retrieve_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = get_expense(
        db=db,
        user_id=current_user.id,
        expense_id=expense_id
    )

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense


# ---------------- UPDATE ----------------
@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse
)
def update_expense_endpoint(
    expense_id: UUID,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = update_expense(
        db=db,
        user_id=current_user.id,
        expense_id=expense_id,
        data=data
    )

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense


# ---------------- SOFT DELETE ----------------
@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_expense_endpoint(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = delete_expense(
        db=db,
        user_id=current_user.id,
        expense_id=expense_id
    )

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return