import unittest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from src.database_utils.connection import DatabaseConnection
from src.services.coin_service import CoinService
from src.models.coin import Coin as SQLAlchemyCoin


class TestCoinService(unittest.IsolatedAsyncioTestCase):

    async def test_get_coin_by_id_found(self):
        mock_coin = SQLAlchemyCoin(id="test_coin", name="Test Coin")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_coin
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = mock_result

        result: SQLAlchemyCoin | None = await CoinService.get_coin_by_id(
            mock_session, "test_coin"
        )

        self.assertEqual(result, mock_coin)
        self.assertTrue(mock_session.execute.called)

    @patch("src.services.coin_service.logger")
    async def test_get_coin_by_id_not_found(self, mock_logger):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.return_value = mock_result

        result: SQLAlchemyCoin | None = await CoinService.get_coin_by_id(
            mock_session, "nonexistent_coin"
        )

        self.assertIsNone(result)
        mock_session.execute.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Coin with id nonexistent_coin not found"
        )


class TestCoinServiceIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = TestClient(app)
        self.db_connection = DatabaseConnection()
        self.session = self.db_connection.async_session()

    async def asyncTearDown(self):
        await self.session.close()

    async def test_create_and_get_coin(self):
        # Create a new coin
        response = self.client.post(
            "/coins/", json={"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
        )
        self.assertEqual(response.status_code, 201)

        # Retrieve the coin by ID
        coin: SQLAlchemyCoin | None = await CoinService.get_coin_by_id(
            self.session, "bitcoin"
        )
        self.assertIsNotNone(coin)
        if coin is not None:
            self.assertEqual(coin.id, "bitcoin")
            self.assertEqual(coin.symbol, "btc")
            self.assertEqual(coin.name, "Bitcoin")
        else:
            self.fail("Coin not found")

    async def test_get_nonexistent_coin(self):
        # Attempt to retrieve a nonexistent coin
        response = self.client.get("/coins/nonexistent_coin")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
