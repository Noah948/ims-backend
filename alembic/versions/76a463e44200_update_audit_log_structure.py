"""update audit log structure

Revision ID: 76a463e44200
Revises: 750bd14c2918
Create Date: 2026-02-21 15:25:25.751241
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '76a463e44200'
down_revision: Union[str, Sequence[str], None] = '750bd14c2918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Ensure pgcrypto exists for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.add_column(
        'audit_logs',
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'audit_logs',
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column('audit_logs', sa.Column('ip_address', sa.Text(), nullable=True))
    op.add_column('audit_logs', sa.Column('user_agent', sa.Text(), nullable=True))
    op.add_column(
        'audit_logs',
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        )
    )
    op.add_column('audit_logs', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))

    # ✅ FIXED HERE
    op.alter_column(
        'audit_logs',
        'id',
        existing_type=sa.UUID(),
        server_default=sa.text('gen_random_uuid()'),
        existing_nullable=False
    )

    op.alter_column(
        'audit_logs',
        'entity_type',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.Text(),
        existing_nullable=False
    )

    op.alter_column(
        'audit_logs',
        'operation',
        existing_type=sa.VARCHAR(length=20),
        type_=sa.Text(),
        existing_nullable=False
    )

    op.drop_index(op.f('ix_audit_logs_entity_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')

    op.create_index(
        'ix_audit_logs_entity',
        'audit_logs',
        ['entity_type', 'entity_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index('ix_audit_logs_entity', table_name='audit_logs')

    op.create_index(
        op.f('ix_audit_logs_entity_type'),
        'audit_logs',
        ['entity_type'],
        unique=False
    )

    op.create_index(
        op.f('ix_audit_logs_entity_id'),
        'audit_logs',
        ['entity_id'],
        unique=False
    )

    op.alter_column(
        'audit_logs',
        'operation',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False
    )

    op.alter_column(
        'audit_logs',
        'entity_type',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False
    )

    op.alter_column(
        'audit_logs',
        'id',
        existing_type=sa.UUID(),
        server_default=None,
        existing_nullable=False
    )

    op.drop_column('audit_logs', 'deleted_at')
    op.drop_column('audit_logs', 'updated_at')
    op.drop_column('audit_logs', 'user_agent')
    op.drop_column('audit_logs', 'ip_address')
    op.drop_column('audit_logs', 'new_values')
    op.drop_column('audit_logs', 'old_values')