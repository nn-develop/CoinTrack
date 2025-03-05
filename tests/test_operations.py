import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
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


if __name__ == "__main__":
    unittest.main()
