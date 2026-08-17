import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Make `backend/` importable so `app.*` resolves regardless of cwd.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings  # noqa: E402
from app.models import Base  # noqa: E402

# Alembic Config object, providing access to alembic.ini values.
config = context.config

# Inject the URL from our settings instead of hardcoding it in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set up loggers from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for --autogenerate support.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a DBAPI connection, emitting SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live connection to the database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _main() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


_main()