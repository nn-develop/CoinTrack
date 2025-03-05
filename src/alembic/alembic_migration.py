import asyncio
import os
from alembic.config import Config
from alembic import command
from src.logger import logger


async def run_alembic_migrations():
    """Run Alembic migrations asynchronously."""
    logger.info("Running Alembic migrations...")
    alembic_cfg = Config("alembic.ini")

    # Check if migrations directory exists, create it if it doesn't
    migrations_dir = "src/alembic/versions"
    os.makedirs(migrations_dir, exist_ok=True)

    try:
        # For a new database, first initialize the database with the current model
        # without creating a migration file
        logger.info("Initializing database schema...")
        await asyncio.to_thread(command.stamp, alembic_cfg, "head")

        # Create a migration file for future changes
        logger.info("Generating migration file...")
        await asyncio.to_thread(
            command.revision,
            alembic_cfg,
            autogenerate=True,
            message="Auto-generated migration",
        )

        # Run the migration to apply any pending changes
        logger.info("Running migration...")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    except Exception as e:
        logger.error(f"Error during Alembic migrations: {e}")
        # If something goes wrong, a simpler approach - just create the tables directly
        logger.info("Falling back to basic migration...")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    logger.info("Alembic migrations completed successfully.")
