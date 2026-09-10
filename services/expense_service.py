from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from datetime import datetime, timedelta, UTC

from scheduler.policies import EXPENSE_RETENTION_DAYS

from models.expense import Expense
from schema.expense import ExpenseCreate, ExpenseUpdate, ExpenseFilter


def create_expense(db: Session, business_id: UUID, data: ExpenseCreate):
    try:
        expense = Expense(
            id=uuid4(),
            business_id=business_id,
            title=data.title,
            amount=data.amount,
            expense_date=data.expense_date,
            is_recurring=data.is_recurring,
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    except Exception:
        db.rollback()
        raise


def get_expenses(db: Session, business_id: UUID):
    stmt = (
        select(Expense)
        .where(Expense.business_id == business_id)
        .where(Expense.deleted_at.is_(None))
        .order_by(Expense.expense_date.desc())
    )

    return db.execute(stmt).scalars().all()


def get_expense(
    db: Session,
    business_id: UUID,
    expense_id: UUID,
):
    stmt = (
        select(Expense)
        .where(Expense.id == expense_id)
        .where(Expense.business_id == business_id)
        .where(Expense.deleted_at.is_(None))
    )

    expense = db.execute(stmt).scalar_one_or_none()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    return expense


def update_expense(
    db: Session,
    business_id: UUID,
    expense_id: UUID,
    data: ExpenseUpdate,
):
    try:
        stmt = (
            select(Expense)
            .where(Expense.id == expense_id)
            .where(Expense.business_id == business_id)
            .where(Expense.deleted_at.is_(None))
        )

        expense = db.execute(stmt).scalar_one_or_none()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(expense, field, value)

        db.commit()
        db.refresh(expense)

        return expense

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise


def delete_expense(
    db: Session,
    business_id: UUID,
    expense_id: UUID,
):
    try:
        stmt = (
            select(Expense)
            .where(Expense.id == expense_id)
            .where(Expense.business_id == business_id)
            .where(Expense.deleted_at.is_(None))
        )

        expense = db.execute(stmt).scalar_one_or_none()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found",
            )

        expense.deleted_at = datetime.now(UTC)

        db.commit()

        return expense

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise


def cleanup_deleted_expenses(db: Session):
    cutoff = datetime.now(UTC) - timedelta(
        days=EXPENSE_RETENTION_DAYS
    )

    (
        db.query(Expense)
        .filter(
            Expense.deleted_at.is_not(None),
            Expense.deleted_at < cutoff,
        )
        .delete(synchronize_session=False)
    )

    db.commit()


def get_expenses_with_filters(
    db: Session,
    business_id: UUID,
    filters: ExpenseFilter,
):
    stmt = select(Expense).where(
        Expense.business_id == business_id,
        Expense.deleted_at.is_(None),
    )

    conditions = []

    if filters.date:
        if filters.date.from_date:
            conditions.append(
                Expense.expense_date >= filters.date.from_date
            )

        if filters.date.to_date:
            conditions.append(
                Expense.expense_date <= filters.date.to_date
            )

    if filters.amount:
        if filters.amount.min is not None:
            conditions.append(
                Expense.amount >= filters.amount.min
            )

        if filters.amount.max is not None:
            conditions.append(
                Expense.amount <= filters.amount.max
            )

    if filters.is_recurring is not None:
        conditions.append(
            Expense.is_recurring == filters.is_recurring
        )

    if filters.search:
        conditions.append(
            Expense.title.ilike(f"%{filters.search}%")
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    stmt = stmt.order_by(Expense.expense_date.desc())

    return db.execute(stmt).scalars().all()