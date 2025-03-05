from src.redis_cache.redis_cache import RedisCache
from src.coingecko.coingecko_coins_api import CoinGeckoAPI
from src.schemas.coin import CoinUpdate


class CoinUpdateService:
    def __init__(self):
        self.redis_cache = RedisCache()
        self.coingecko_api = CoinGeckoAPI()

    async def update_coin_data(self, coin_data: CoinUpdate) -> CoinUpdate:
        try:
            # Check Redis cache
            cached_data: dict[str, str] = self.redis_cache.get_coin_from_cache(
                coin_data.id
            )
            if cached_data:
                # Update coin_data with cached values if they differ
                if (
                    cached_data.get("symbol")
                    and cached_data["symbol"] != coin_data.symbol
                ):
                    coin_data.symbol = cached_data["symbol"]
                if cached_data.get("name") and cached_data["name"] != coin_data.name:
                    coin_data.name = cached_data["name"]
                return coin_data
            else:
                # Fetch data from CoinGecko API
                api_data: dict = self.coingecko_api.get_coin_info(coin_data.id)
                if api_data:
                    if (
                        api_data.get("symbol")
                        and api_data["symbol"] != coin_data.symbol
                    ):
                        coin_data.symbol = api_data["symbol"]
                    if api_data.get("name") and api_data["name"] != coin_data.name:
                        coin_data.name = api_data["name"]
                    # Store fetched data into Redis cache
                    if coin_data.symbol and coin_data.name:
                        self.redis_cache.set_coin_cache(
                            coin_data.id, coin_data.symbol, coin_data.name
                        )
                    return coin_data
                else:
                    raise ValueError(
                        f"Coin ID {coin_data.id} not found in CoinGecko API"
                    )
        except ValueError as e:
            raise ValueError(
                f"Coin ID {coin_data.id} not found in cache or CoinGecko API"
            )
