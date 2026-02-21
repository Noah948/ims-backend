from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4
from uuid import UUID
from datetime import datetime

from models.expense import Expense
from schema.expense import ExpenseCreate, ExpenseUpdate


# ---------------- CREATE ----------------
def create_expense(db: Session, user_id: UUID, data: ExpenseCreate):
    try:
        expense = Expense(
            id=uuid4(),
            user_id=user_id,
            title=data.title,
            amount=data.amount,
            expense_date=data.expense_date,
            description=data.description,
            is_recurring=data.is_recurring,
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense, None

    except Exception:
        db.rollback()
        raise


# ---------------- READ ALL ----------------
def get_expenses(db: Session, user_id: UUID):
    stmt = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
        .order_by(Expense.expense_date.desc())
    )
    return db.execute(stmt).scalars().all()


# ---------------- READ SINGLE ----------------
def get_expense(db: Session, user_id: UUID, expense_id: UUID):
    stmt = (
        select(Expense)
        .where(Expense.id == expense_id)
        .where(Expense.user_id == user_id)
        .where(Expense.deleted_at.is_(None))
    )
    return db.execute(stmt).scalar_one_or_none()


# ---------------- UPDATE ----------------
def update_expense(
    db: Session,
    user_id: UUID,
    expense_id: UUID,
    data: ExpenseUpdate
):
    try:
        stmt = (
            select(Expense)
            .where(Expense.id == expense_id)
            .where(Expense.user_id == user_id)
            .where(Expense.deleted_at.is_(None))
        )
        expense = db.execute(stmt).scalar_one_or_none()

        if not expense:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(expense, field, value)

        db.commit()
        db.refresh(expense)
        return expense

    except Exception:
        db.rollback()
        raise


# ---------------- SOFT DELETE ----------------
def delete_expense(db: Session, user_id: UUID, expense_id: UUID):
    try:
        stmt = (
            select(Expense)
            .where(Expense.id == expense_id)
            .where(Expense.user_id == user_id)
            .where(Expense.deleted_at.is_(None))
        )
        expense = db.execute(stmt).scalar_one_or_none()

        if not expense:
            return None

        expense.deleted_at = datetime.utcnow()

        db.commit()
        return expense

    except Exception:
        db.rollback()
        raise