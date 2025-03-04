import asyncio
from src.logger import setup_logging, logger
from src.database_utils.connection import DatabaseConnection
from src.database_utils.operations import DatabaseOperations

DEFAULT_TIMEOUT = 40


class PostgresDatabaseManager:
    def __init__(self):
        self.connection = DatabaseConnection()
        self.operations = DatabaseOperations(self.connection)

    async def manage_database(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Main function to manage the PostgreSQL database."""
        if not await self.connection.wait_for_postgres(timeout):
            logger.error(
                f"Error: PostgreSQL server is not available after waiting for {timeout} seconds."
            )
            return

        try:
            engine = self.connection.engine
            if engine:
                await engine.dispose()

            postgres_conn = await self.connection.create_direct_connection("postgres")

            try:
                db_exists = await postgres_conn.fetchval(
                    f"SELECT 1 FROM pg_database WHERE datname = '{self.connection.dbname}'"
                )

                if db_exists:
                    logger.info(
                        f"Database '{self.connection.dbname}' already exists, preserving existing data."
                    )
                else:
                    logger.info(
                        f"Database '{self.connection.dbname}' doesn't exist, creating it."
                    )
                    await self.operations.create_database()
                    async with self.connection.async_session() as session:
                        await self.operations.create_coin_table(session)
                        logger.info("New database with tables created successfully.")
            finally:
                await postgres_conn.close()

            if db_exists:
                logger.info("Using existing database structure and data.")

        except Exception as e:
            logger.error(f"Error during database initialization: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    # Initialize the logger before using it
    setup_logging()
    manager = PostgresDatabaseManager()
    asyncio.run(manager.manage_database(timeout=40))
