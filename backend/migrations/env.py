from logging.config import fileConfig
import os
import logging

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# Import the Base metadata and settings
from app.models.database import Base
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Construct absolute path for the database
if settings.DATABASE_URL.startswith('sqlite:///./'):
    db_relative_path = settings.DATABASE_URL.split('///./')[1]
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', db_relative_path))
    db_url = f'sqlite:///{db_path}'
else:
    db_url = settings.DATABASE_URL

# Replace aiosqlite with sqlite for synchronous migration
db_url = db_url.replace('+aiosqlite', '')

logger.debug(f"Database URL for migrations: {db_url}")

# Set the database URL in the Alembic configuration
config.set_main_option("sqlalchemy.url", db_url)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    logger.debug(f"Offline migration URL: {url}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    try:
        # Create engine directly instead of using engine_from_config
        connectable = create_engine(
            db_url,
            poolclass=pool.NullPool,
        )

        logger.debug(f"Created engine for URL: {db_url}")

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()

    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)
        raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
