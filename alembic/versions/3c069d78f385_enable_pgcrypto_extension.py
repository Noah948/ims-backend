"""enable pgcrypto extension

Revision ID: 3c069d78f385
Revises: b2ec524123b5
Create Date: 2026-01-27 15:03:39.088110
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c069d78f385"
down_revision: Union[str, Sequence[str], None] = "b2ec524123b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgcrypto for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')


def downgrade() -> None:
    # Optional: remove pgcrypto
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
