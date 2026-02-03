# alembic/versions/0001_create_users_table.py

from alembic import op
import sqlalchemy as sa

revision = "0001_create_users_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # IMPORTANT: ensure pgcrypto exists (for gen_random_uuid)
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),

        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),

        sa.Column(
            "role",
            sa.String(),
            nullable=False,
            server_default="owner",
        ),

        sa.Column(
            "business_name",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "business_type",
            sa.String(),
            nullable=False,
            server_default="general",
        ),

        sa.Column(
            "name",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "contact_number",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "avatar",
            sa.String(),
            nullable=True,
        ),

        sa.Column(
            "notifications_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column("subscription_start_date", sa.TIMESTAMP(), nullable=True),
        sa.Column("subscription_end_date", sa.TIMESTAMP(), nullable=True),

        sa.Column(
            "total_products",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "out_of_stock_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "low_stock_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column("last_active_at", sa.TIMESTAMP(), nullable=True),

        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
    )

    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade():
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
