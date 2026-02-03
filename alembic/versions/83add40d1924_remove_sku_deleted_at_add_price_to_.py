"""remove sku and deleted_at, add price to products

Revision ID: 83add40d1924
Revises: 3c069d78f385
Create Date: 2026-02-03 16:30:18.136265
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "83add40d1924"
down_revision: Union[str, Sequence[str], None] = "3c069d78f385"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema:
    - remove sku
    - remove deleted_at
    - add price (NUMERIC)
    """

    # 🔹 remove sku column
    op.drop_column("products", "sku")

    # 🔹 remove deleted_at column
    op.drop_column("products", "deleted_at")

    # 🔹 add price column
    op.add_column(
        "products",
        sa.Column("price", sa.Numeric(10, 2), nullable=False)
    )


def downgrade() -> None:
    """
    Downgrade schema:
    - remove price
    - restore deleted_at
    - restore sku + unique constraint
    """

    # 🔹 remove price
    op.drop_column("products", "price")

    # 🔹 restore deleted_at
    op.add_column(
        "products",
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True)
    )

    # 🔹 restore sku
    op.add_column(
        "products",
        sa.Column("sku", sa.TEXT(), nullable=False)
    )

    # 🔹 restore unique constraint on sku
    op.create_unique_constraint(
        "products_sku_key",
        "products",
        ["sku"]
    )
