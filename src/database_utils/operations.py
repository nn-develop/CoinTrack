from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from src.logger import setup_logging, logger
from src.database_utils.connection import DatabaseConnection
from src.models import Coin


class DatabaseOperations:
    def __init__(self):
        self.connection: DatabaseConnection = DatabaseConnection()

    async def check_database_exists(self, session: AsyncSession) -> bool:
        """Check if the database already exists."""
        result = await session.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{self.connection.dbname}'"
        )
        return result.scalar() is not None

    async def drop_database(self, session: AsyncSession) -> None:
        """Drop the database if it exists."""
        logger.info(f"Dropping database '{self.connection.dbname}'...")
        await session.execute(f"DROP DATABASE IF EXISTS {self.connection.dbname}")

    async def create_database(self, session: AsyncSession) -> None:
        """Create the database if it doesn't exist."""
        logger.info(f"Creating database '{self.connection.dbname}'...")
        await session.execute(f"CREATE DATABASE {self.connection.dbname}")
        await session.execute(
            f"GRANT ALL PRIVILEGES ON DATABASE {self.connection.dbname} TO {self.connection.user};"
        )

    async def create_coin_table(self, session: AsyncSession) -> None:
        """Create a table with the specified structure."""
        logger.info(f"Creating table 'coin' in database '{self.connection.dbname}'...")
        async with self.connection.engine.begin() as conn:
            await conn.run_sync(Coin.metadata.create_all)

    async def insert_coin_data(self, session: AsyncSession, data: list[dict]) -> None:
        """Insert coin data into the coin table."""
        logger.info(f"Inserting coin data into table 'coin'...")
        async with session.begin():
            for record in data:
                coin: Coin = Coin(**record)
                session.add(coin)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                logger.error("Failed to insert coin data due to integrity error.")
