from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- CUSTOM CONFIGURATION START ---
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables from .env
load_dotenv()

# Import Base from our models/database layer so Alembic can read the metadata
from app.database import Base
from app.config import get_settings

settings = get_settings()
target_metadata = Base.metadata

# Overwrite the sqlalchemy.url value in the alembic.ini config
# with the URL from our environment/settings
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)
# --- CUSTOM CONFIGURATION END ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
