import requests
from src.logger import logger


class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()

    def get_coin_info(self, coin_id: str) -> dict:
        """
        Fetch basic information about a cryptocurrency from CoinGecko API.
        """
        url: str = f"{self.BASE_URL}/coins/{coin_id}"
        try:
            response: requests.Response = self.session.get(url)
            response.raise_for_status()
            logger.info(f"Fetched data for {coin_id} from CoinGecko API.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from CoinGecko API: {e}")
            return {}

    def get_coin_list(self) -> list:
        """
        Fetch a list of all available cryptocurrencies from CoinGecko API.
        """
        url: str = f"{self.BASE_URL}/coins/list"
        try:
            response: requests.Response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching coin list from CoinGecko API: {e}")
            return []
