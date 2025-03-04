import requests
from src.logger import setup_logging, logger


class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()

    def get_coin_info(self, coin_id: str) -> dict:
        """
        Fetch basic information about a cryptocurrency from CoinGecko API.

        :param coin_id: The ID of the cryptocurrency (e.g., 'bitcoin').
        :return: A dictionary containing the cryptocurrency information.
        """
        url: str = f"{self.BASE_URL}/coins/{coin_id}"
        try:
            response: requests.Response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from CoinGecko API: {e}")
            return {}

    def get_coin_list(self) -> list:
        """
        Fetch a list of all available cryptocurrencies from CoinGecko API.

        :return: A list of dictionaries, each containing the ID and name of a cryptocurrency.
        """
        url: str = f"{self.BASE_URL}/coins/list"
        try:
            response: requests.Response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching coin list from CoinGecko API: {e}")
            return []


# Example usage
if __name__ == "__main__":
    setup_logging()
    api = CoinGeckoAPI()
    coin_list = api.get_coin_list()
    # print(coin_list)
    coin_info = api.get_coin_info("ethereum")
    print(coin_info)
