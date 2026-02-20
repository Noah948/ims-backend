from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# 🔹 Make project root importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🔹 Import Base and models
from core.database import Base
import models.user_model  # IMPORTANT: load models
import models.team
import models.job
import models.category
import models.product
import models.sale
import models.payment
import models.audit_log

# 🔹 Alembic config
config = context.config

# 🔹 Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 🔹 Metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,      # detects column type changes
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
