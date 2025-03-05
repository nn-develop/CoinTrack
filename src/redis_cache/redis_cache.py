import redis
import os
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()


class RedisCache:
    def __init__(self, db_index: int = int(os.getenv("REDIS_DB", 0))):
        host: str = os.getenv("REDIS_HOST", "localhost")
        port: int = int(os.getenv("REDIS_PORT", 6379))
        db: int = db_index
        self.client = redis.Redis(host=host, port=port, db=db)

    def clear_cache(self) -> None:
        """
        Clear the entire Redis cache.
        """
        try:
            self.client.flushdb()
            logger.info("Cleared the entire Redis cache")
        except redis.RedisError as e:
            logger.error(f"Error clearing the Redis cache: {e}")

    def set_coin_cache(self, id: str, symbol: str, name: str) -> None:
        """
        Set a value in the Redis hash.
        """
        try:
            value: dict[str, str] = {"symbol": symbol, "name": name}
            self.client.hset(id, mapping=value)
            logger.info(f"Set cache for id: {id}")
        except redis.RedisError as e:
            logger.error(f"Error setting cache for id {id}: {e}")

    def get_coin_from_cache(self, id: str) -> dict[str, str]:
        """
        Get all data for a given coin ID from the Redis hash.
        """
        try:
            data: dict[str, str] | None = self.is_coin_in_cache(id)
            if data:
                return data
            else:
                return {}
        except redis.RedisError as e:
            logger.error(f"Error retrieving cache for id {id}: {e}")
            return {}

    def is_coin_in_cache(self, id: str) -> dict[str, str] | None:
        """
        Check if a coin with a specific ID is in the cache.
        """
        try:
            data = self.client.hgetall(id)
            if data:
                return {
                    key.decode("utf-8"): value.decode("utf-8")
                    for key, value in data.items()
                }
            else:
                return None
        except redis.RedisError as e:
            logger.error(f"Error retrieving cache for id {id}: {e}")
            return None
