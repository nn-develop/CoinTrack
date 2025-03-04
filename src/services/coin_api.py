from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from src.database_utils.connection import DatabaseConnection
from src.database_utils.operations import DatabaseOperations
from src.models import Coin as SQLAlchemyCoin

app = FastAPI()
db_connection = DatabaseConnection()
db_operations = DatabaseOperations()


class CoinBase(BaseModel):
    id: str
    symbol: str
    name: str
    target_price: float | None = None

    class Config:
        from_attributes = True


class CoinCreate(CoinBase):
    pass


class CoinUpdate(BaseModel):
    id: str | None = Field(default=None)
    symbol: str | None = Field(default=None)
    name: str | None = Field(default=None)
    target_price: float | None = Field(default=None)


async def get_coin_by_id(session: AsyncSession, coin_id: str) -> SQLAlchemyCoin:
    try:
        result = await session.execute(select(SQLAlchemyCoin).filter_by(id=coin_id))
        coin = result.scalar_one()
        return coin
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Coin not found")


@app.post(
    "/coins/",
    response_model=CoinBase,
    responses={201: {"description": "Coin created successfully"}},
)
async def create_coin(coin: CoinCreate):
    async with db_connection.async_session() as session:
        await db_operations.insert_coin_data(session, [coin.dict()])
    return coin


@app.get(
    "/coins/{coin_id}",
    response_model=CoinBase,
    responses={404: {"description": "Coin not found"}},
)
async def get_coin(coin_id: str):
    async with db_connection.async_session() as session:
        coin = await get_coin_by_id(session, coin_id)
        return coin


@app.put(
    "/coins/{coin_id}",
    response_model=CoinBase,
    responses={404: {"description": "Coin not found"}},
)
async def update_coin(coin_id: str, coin: CoinUpdate):
    async with db_connection.async_session() as session:
        existing_coin: SQLAlchemyCoin = await get_coin_by_id(session, coin_id)
        update_data = coin.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_coin, key, value)
        await session.commit()
    return existing_coin


@app.delete(
    "/coins/{coin_id}",
    responses={
        404: {"description": "Coin not found"},
        200: {"description": "Coin deleted successfully"},
    },
)
async def delete_coin(coin_id: str):
    async with db_connection.async_session() as session:
        coin = await get_coin_by_id(session, coin_id)
        await session.delete(coin)
        await session.commit()
    return {"message": "Coin deleted successfully"}


@app.get("/coins/", response_model=list[CoinBase])
async def list_coins():
    async with db_connection.async_session() as session:
        result = await session.execute(select(SQLAlchemyCoin))
        coins = result.scalars().all()
        return coins
