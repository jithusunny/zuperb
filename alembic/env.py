from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from app.models import Base  # Import your Base metadata
from dotenv import load_dotenv  # For loading .env files

# Load .env file
load_dotenv()

# Get the DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Alembic Config object
config = context.config

# Update the sqlalchemy.url in Alembic config dynamically
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Metadata for Alembic migrations
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
