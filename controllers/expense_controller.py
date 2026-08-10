from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from services.expense_service import (
    create_expense as create_expense_service,
    get_expenses as get_expenses_service,
    get_expense as get_expense_service,
    update_expense as update_expense_service,
    delete_expense as delete_expense_service,
    get_expenses_with_filters,
)
from schema.expense import ExpenseCreate, ExpenseUpdate, ExpenseFilter


def create_expense(db: Session, business_id: UUID, data: ExpenseCreate):
    expense, _ = create_expense_service(db, business_id, data)
    return expense


def get_expenses(db: Session, business_id: UUID):
    return get_expenses_service(db, business_id)


def get_expense(db: Session, business_id: UUID, expense_id: UUID):
    expense = get_expense_service(db, business_id, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


def update_expense(db: Session, business_id: UUID, expense_id: UUID, data: ExpenseUpdate):
    expense = update_expense_service(db, business_id, expense_id, data)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


def delete_expense(db: Session, business_id: UUID, expense_id: UUID):
    expense = delete_expense_service(db, business_id, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None


def filter_expenses(db: Session, business_id: UUID, filters: ExpenseFilter):
    return get_expenses_with_filters(db, business_id, filters)