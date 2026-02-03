"""merge migration heads

Revision ID: 0e64429605dc
Revises: 5d2a573c06b0, 0001_create_users_table
Create Date: 2026-01-27 14:47:31.338540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e64429605dc'
down_revision: Union[str, Sequence[str], None] = ('5d2a573c06b0', '0001_create_users_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
