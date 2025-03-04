import asyncio
from src.coingecko.coingecko_coins_api import CoinGeckoAPI
from src.redis_cache.redis_cache import RedisCache
from src.logger import setup_logging, logger


class PeriodicCoinDataUpdater:
    def __init__(self, interval: int = 86400, batch_size: int = 100):
        self.api = CoinGeckoAPI()
        self.cache = RedisCache()
        self.interval: int = interval
        self.batch_size: int = batch_size
        self.stop_event = asyncio.Event()

    async def fetch_coin_list(self) -> list:
        logger.info("Fetching coin list from CoinGecko API...")
        return self.api.get_coin_list()

    async def cache_coin_data(self, coin_list: list) -> None:
        logger.info("Caching coin data...")
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        tasks: list = []
        for coin in coin_list:
            coin_id: str = coin.get("id")
            coin_symbol: str = coin.get("symbol")
            coin_name: str = coin.get("name")
            if coin_id and coin_symbol and coin_name:
                tasks.append(
                    loop.run_in_executor(
                        None, self.cache.set_coin_cache, coin_id, coin_symbol, coin_name
                    )
                )
        await asyncio.gather(*tasks)
        logger.info("Coin data cached successfully.")

    async def fetch_and_cache_coin_data(self):
        coin_list: list = await self.fetch_coin_list()
        for i in range(0, len(coin_list), self.batch_size):
            batch: list = coin_list[i : i + self.batch_size]
            await self.cache_coin_data(batch)
            await asyncio.sleep(1)  # to reduce load

    async def periodic_task(self):
        while not self.stop_event.is_set():
            await self.fetch_and_cache_coin_data()
            await asyncio.sleep(self.interval)

    def stop(self):
        self.stop_event.set()


if __name__ == "__main__":
    setup_logging()
    updater = PeriodicCoinDataUpdater(
        interval=86400, batch_size=100
    )  # 86400 seconds = 24 hours
    try:
        asyncio.run(updater.periodic_task())
    except KeyboardInterrupt:
        updater.stop()
        logger.info("Periodic coin data updater stopped.")
