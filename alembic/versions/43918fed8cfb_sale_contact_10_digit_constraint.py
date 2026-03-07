"""sale contact 10 digit constraint

Revision ID: 43918fed8cfb
Revises: 52da84bc91c3
Create Date: 2026-03-05 14:29:22.898759
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "43918fed8cfb"
down_revision: Union[str, Sequence[str], None] = "52da84bc91c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Make contact NOT NULL
    op.alter_column(
        "jobs",
        "contact",
        existing_type=sa.TEXT(),
        nullable=False
    )

    op.alter_column(
        "sales",
        "contact",
        existing_type=sa.TEXT(),
        nullable=False
    )

    # Add 10-digit validation constraints
    op.create_check_constraint(
        "ck_jobs_contact_10_digits",
        "jobs",
        "contact ~ '^[0-9]{10}$'"
    )

    op.create_check_constraint(
        "ck_sales_contact_10_digits",
        "sales",
        "contact ~ '^[0-9]{10}$'"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove constraints
    op.drop_constraint(
        "ck_sales_contact_10_digits",
        "sales",
        type_="check"
    )

    op.drop_constraint(
        "ck_jobs_contact_10_digits",
        "jobs",
        type_="check"
    )

    # Make contact nullable again
    op.alter_column(
        "sales",
        "contact",
        existing_type=sa.TEXT(),
        nullable=True
    )

    op.alter_column(
        "jobs",
        "contact",
        existing_type=sa.TEXT(),
        nullable=True
    )