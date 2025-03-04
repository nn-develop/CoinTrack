from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import asyncio
from src.logger import logger
from src.models import Coin
from src.database_utils.connection import DatabaseConnection


class DatabaseOperations:
    def __init__(self, connection: DatabaseConnection | None = None):
        """
        Initialize database operations with a connection.

        Args:
            connection: DatabaseConnection instance. If None, creates a new connection.
        """
        self.connection: DatabaseConnection = connection or DatabaseConnection()

    async def check_database_exists(self, session: AsyncSession) -> bool:
        """Check if the database already exists."""
        result = await session.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{self.connection.dbname}'"
        )
        return result.scalar() is not None

    async def drop_database(self) -> None:
        """Drop the database if it exists."""
        logger.info(f"Dropping database '{self.connection.dbname}'...")
        try:
            # Terminate all existing connections to the database
            await self.connection.terminate_database_connections(self.connection.dbname)

            await self.connection.execute_outside_transaction(
                f"DROP DATABASE IF EXISTS {self.connection.dbname}"
            )
        except Exception as e:
            logger.error(f"Failed to drop database '{self.connection.dbname}': {e}")
            raise

    async def create_database(self) -> None:
        """Create the database."""
        logger.info(f"Creating database '{self.connection.dbname}'...")
        await self.connection.execute_outside_transaction(
            f"CREATE DATABASE {self.connection.dbname}"
        )
        await self.connection.execute_outside_transaction(
            f"GRANT ALL PRIVILEGES ON DATABASE {self.connection.dbname} TO {self.connection.user}"
        )


# Example of creating a table and inserting data withouth using ORM
# async def create_coin_table(self, session: AsyncSession) -> None:
#     """Create a table with the specified structure."""
#     logger.info(f"Creating table 'coin' in database '{self.connection.dbname}'...")
#     async with self.connection.engine.begin() as conn:
#         await conn.run_sync(Coin.metadata.create_all)

# async def insert_coin_data(self, session: AsyncSession, data: list[dict]) -> None:
#     """Insert coin data into the coin table."""
#     logger.info(f"Inserting coin data into table 'coin'...")
#     async with session.begin():
#         for record in data:
#             coin: Coin = Coin(**record)
#             session.add(coin)
#         try:
#             await session.commit()
#         except IntegrityError:
#             await session.rollback()
#             logger.error("Failed to insert coin data due to integrity error.")


# Example usage
async def main():
    # Database connection setup
    db_connection = DatabaseConnection()
    async_session = db_connection.async_session

    # Wait for PostgreSQL server to be available
    if not await db_connection.wait_for_postgres(timeout=60):
        return

    # Create an instance of DatabaseOperations with the connection
    db_ops = DatabaseOperations(db_connection)

    # Drop the database if it exists
    await db_ops.drop_database()

    # Now create the database
    await db_ops.create_database()
    # For operations on tables, we need a session
    # async with async_session() as session:
    #     await db_ops.create_coin_table(session)


# Run the example
if __name__ == "__main__":
    asyncio.run(main())
