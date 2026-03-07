"""update user model fields

Revision ID: 52da84bc91c3
Revises: f31b977e19a8
Create Date: 2026-03-05
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '52da84bc91c3'
down_revision: Union[str, Sequence[str], None] = 'f31b977e19a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Rename column instead of dropping (preserves data)
    op.alter_column('users', 'name', new_column_name='user_name')

    # Create index + unique constraint for contact
    op.create_index('ix_users_contact', 'users', ['contact_number'])
    op.create_unique_constraint(
        "uq_users_contact_number",
        "users",
        ["contact_number"]
    )

    # Drop unused columns
    op.drop_column('users', 'business_type')
    op.drop_column('users', 'last_active_at')
    op.drop_column('users', 'notifications_enabled')


def downgrade() -> None:
    """Downgrade schema."""

    # Recreate dropped columns
    op.add_column(
        'users',
        sa.Column(
            'notifications_enabled',
            sa.Boolean(),
            server_default=sa.text('true'),
            nullable=False
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'business_type',
            sa.Text(),
            server_default=sa.text("'general'::text"),
            nullable=False
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'last_active_at',
            postgresql.TIMESTAMP(),
            nullable=True
        )
    )

    # Remove constraints
    op.drop_constraint("uq_users_contact_number", "users", type_='unique')
    op.drop_index('ix_users_contact', table_name='users')

    # Rename back
    op.alter_column('users', 'user_name', new_column_name='name')