from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.coin import Coin as SQLAlchemyCoin
from src.logger import logger


class CoinService:

    @staticmethod
    async def get_coin_by_id(
        session: AsyncSession, coin_id: str
    ) -> SQLAlchemyCoin | None:
        result = await session.execute(select(SQLAlchemyCoin).filter_by(id=coin_id))
        coin = result.scalar_one_or_none()
        if coin is None:
            logger.error(f"Coin with id {coin_id} not found")
        return coin

    @staticmethod
    async def handle_coin_not_found(session: AsyncSession, coin_id: str):
        coin: SQLAlchemyCoin | None = await CoinService.get_coin_by_id(session, coin_id)
        if not coin:
            raise HTTPException(status_code=404, detail="Coin with this ID not found")
        return coin

    @staticmethod
    async def handle_coin_already_exists(session: AsyncSession, coin_id: str):
        if await CoinService.get_coin_by_id(session, coin_id):
            logger.error(f"Coin with id {coin_id} already exists")
            raise HTTPException(
                status_code=400, detail="Coin with this ID already exists"
            )
