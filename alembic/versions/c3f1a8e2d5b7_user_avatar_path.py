"""users: avatar_path for Supabase storage object key

Revision ID: c3f1a8e2d5b7
Revises: b7e2c4a91f03
Create Date: 2026-10-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f1a8e2d5b7'
down_revision: Union[str, Sequence[str], None] = 'b7e2c4a91f03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_path', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'avatar_path')
