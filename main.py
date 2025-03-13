import asyncio
import unittest
from fastapi import FastAPI
from src.logger import setup_logging, logger
from src.database_utils.connection import DatabaseConnection
from src.database_utils.operations import DatabaseOperations
from src.api.routes.health_routes import router as health_router
from src.api.routes.coin_routes import router as coin_router
from src.alembic.alembic_migration import run_alembic_migrations
from src.services.uvicorn_service import run_uvicorn

setup_logging()

app = FastAPI()

app.include_router(health_router)
app.include_router(coin_router)


async def main():
    # This script is adjusted just for demonstration purposes

    db_connection = DatabaseConnection()
    db_ops = DatabaseOperations(db_connection)

    # 1. Check if PostgreSQL server is ready
    logger.info("Checking if PostgreSQL server is ready...")
    if not await db_connection.wait_for_postgres(timeout=60):
        logger.error("PostgreSQL server is not available. Exiting.")
        return

    logger.info("PostgreSQL server is ready.")

    # 2. Check if database exists
    postgres_conn = await db_connection.create_direct_connection("postgres")
    try:
        db_exists = await postgres_conn.fetchval(
            f"SELECT 1 FROM pg_database WHERE datname = '{db_connection.dbname}'"
        )

        # 3. If database exists, drop it
        if db_exists:
            logger.info(f"Database '{db_connection.dbname}' exists. Dropping it...")
            await db_ops.drop_database()
            logger.info(f"Database '{db_connection.dbname}' dropped successfully.")
    finally:
        await postgres_conn.close()

    # 4. Create a new database
    logger.info(f"Creating database '{db_connection.dbname}'...")
    await db_ops.create_database()
    logger.info(f"Database '{db_connection.dbname}' created successfully.")

    # 5. Run Alembic migrations
    logger.info("Running Alembic migrations...")
    await run_alembic_migrations()
    logger.info("Database setup and migrations completed successfully!")


def run_tests():
    # Just a sample of unit tests
    loader = unittest.TestLoader()
    tests: unittest.TestSuite = loader.discover("tests")
    testRunner = unittest.TextTestRunner()
    testRunner.run(tests)


if __name__ == "__main__":
    run_tests()
    asyncio.run(main())
    run_uvicorn()
