"""update models

Revision ID: b51f645e2ab7
Revises: 
Create Date: 2026-04-11 20:09:59.122745

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b51f645e2ab7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove description column from jobs
    op.drop_column('jobs', 'description')

    # Add location column to users
    op.add_column('users', sa.Column('location', sa.Text(), nullable=True))

    # Create index for location
    op.create_index('ix_users_location', 'users', ['location'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_users_location', table_name='users')

    # Remove location column
    op.drop_column('users', 'location')

    # Add description back (SAFE: nullable=True)
    op.add_column(
        'jobs',
        sa.Column('description', sa.TEXT(), nullable=True)
    )