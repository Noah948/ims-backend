"""dashboard: inventory snapshots + sales time index

Revision ID: b7e2c4a91f03
Revises: dfd7d815ad67
Create Date: 2026-10-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b7e2c4a91f03'
down_revision: Union[str, Sequence[str], None] = 'dfd7d815ad67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'inventory_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('total_units', sa.Integer(), nullable=False),
        sa.Column('stock_value', sa.Numeric(14, 2), nullable=False),
        sa.Column('low_stock', sa.Integer(), nullable=False),
        sa.Column('out_of_stock', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'snapshot_date', name='uq_inventory_snapshots_business_date'),
    )
    op.create_index('ix_sales_business_created', 'sales', ['business_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_sales_business_created', table_name='sales')
    op.drop_table('inventory_snapshots')
