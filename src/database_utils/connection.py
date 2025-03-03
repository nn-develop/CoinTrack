from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import subprocess
import time
import os
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()


class DatabaseConnection:
    def __init__(self):
        """Initialize the database manager, ensuring all required environment variables are set."""
        self.user: str = self._get_env_variable("POSTGRES_USER")
        self.password: str = self._get_env_variable("POSTGRES_PASSWORD")
        self.host: str = self._get_env_variable("POSTGRES_HOST")
        self.port: str = self._get_env_variable("POSTGRES_PORT")
        self.dbname: str = self._get_env_variable("POSTGRES_DB")
        self.database_url: str = (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        )
        self.engine = create_async_engine(self.database_url, echo=True)
        self.async_session: sessionmaker = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def _get_env_variable(self, var_name: str) -> str:
        """Retrieve an environment variable, raising an error if it is not set."""
        value: str | None = os.getenv(var_name)
        if not value:
            raise ValueError(
                f"Environment variable {var_name} is required but not set."
            )
        return value

    async def connect(self) -> AsyncSession:
        """Connect to PostgreSQL database asynchronously."""
        logger.debug(f"Attempting to connect to PostgreSQL database: {self.dbname}")
        return self.async_session()

    async def wait_for_postgres(self, timeout: int, delay: int = 5) -> bool:
        start_time: float = time.time()
        logger.info(f"Waiting for PostgreSQL server at {self.host}:{self.port}...")
        while time.time() - start_time < timeout:
            if (
                subprocess.run(
                    ["nc", "-zv", self.host, self.port],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ).returncode
                == 0
            ):
                logger.info("PostgreSQL server is up!")
                return True
            await asyncio.sleep(delay)
        logger.error(
            f"PostgreSQL server did not become available after {timeout} seconds."
        )
        return False
