from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.database_utils.connection import DatabaseConnection
from src.redis_cache.redis_cache import RedisCache
from src.coingecko.coingecko_coins_api import CoinGeckoAPI
from src.logger import logger


# Závislost pro získání databázové relace
async def get_db() -> AsyncSession:
    db_connection = DatabaseConnection()
    async with db_connection.async_session() as session:
        yield session


# Závislost pro získání Redis klienta
def get_redis() -> RedisCache:
    return RedisCache()


# Závislost pro získání CoinGecko API klienta
def get_coingecko_api() -> CoinGeckoAPI:
    return CoinGeckoAPI()
