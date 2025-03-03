import asyncio
from src.database_utils.connection import DatabaseConnection
from src.database_utils.operations import DatabaseOperations
from src.logger import setup_logging, logger

DEFAULT_TIMEOUT = 40


class PostgresDatabaseManager:
    def __init__(self):
        self.connection = DatabaseConnection()
        self.operations = DatabaseOperations()

    async def manage_database(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Main function to manage the PostgreSQL database."""
        if not await self.connection.wait_for_postgres(timeout):
            logger.error(
                f"Error: PostgreSQL server is not available after waiting for {timeout} seconds."
            )
            return

        try:
            session = await self.connection.connect()
            async with session:
                # Check if the database already exists
                if not await self.operations.check_database_exists(session):
                    await self.operations.drop_database(session)
                    await self.operations.create_database(session)
                else:
                    logger.info(f"Database '{self.connection.dbname}' already exists.")

            await self.operations.create_coin_table(session)

        except Exception as e:
            logger.error(f"Error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    # Initialize the logger before using it
    setup_logging()

    # Create an instance of PostgresDatabaseManager
    manager = PostgresDatabaseManager()

    # Call the function to manage the database
    asyncio.run(manager.manage_database(timeout=40))
