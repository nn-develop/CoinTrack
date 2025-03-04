from fastapi import FastAPI, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.database_utils.connection import DatabaseConnection
from src.models import Coin as SQLAlchemyCoin
from src.schemas.coin import CoinBase, CoinCreate, CoinUpdate
from src.services.coin_update_service import CoinUpdateService
from src.logger import setup_logging, logger
from src.services.periodic_coin_data_updater import PeriodicCoinDataUpdater
from src.api.routes.health_routes import router as health_router

app = FastAPI()
db_connection = DatabaseConnection()
coin_update_service = CoinUpdateService()
periodic_updater = PeriodicCoinDataUpdater()

setup_logging()
app.include_router(health_router)


async def get_coin_by_id(session: AsyncSession, coin_id: str) -> SQLAlchemyCoin | None:
    try:
        result = await session.execute(select(SQLAlchemyCoin).filter_by(id=coin_id))
        coin = result.scalar_one_or_none()
        return coin
    except NoResultFound:
        logger.error(f"Coin with id {coin_id} not found")
        return None


@app.post(
    "/coins/",
    response_model=CoinBase,
    responses={201: {"description": "Coin created successfully"}},
)
async def create_coin(coin: CoinCreate):
    async with db_connection.async_session() as session:
        existing_coin: SQLAlchemyCoin | None = await get_coin_by_id(session, coin.id)
        if existing_coin:
            logger.error(f"Coin with id {coin.id} already exists")
            raise HTTPException(
                status_code=400, detail="Coin with this ID already exists"
            )

        try:
            # Update coin data using CoinUpdateService
            updated_coin_data: CoinUpdate = await coin_update_service.update_coin_data(
                coin.id, coin
            )
            new_coin = SQLAlchemyCoin(**updated_coin_data.dict())
            session.add(new_coin)
            await session.commit()
            await session.refresh(new_coin)
            logger.info(f"Coin with id {coin.id} created successfully")
            return new_coin
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except IntegrityError:
            await session.rollback()
            logger.error(f"Coin with id {coin.id} already exists")
            raise HTTPException(
                status_code=400, detail="Coin with this ID already exists"
            )


@app.get(
    "/coins/{coin_id}",
    response_model=CoinBase,
    responses={404: {"description": "Coin not found"}},
)
async def get_coin(coin_id: str):
    async with db_connection.async_session() as session:
        coin = await get_coin_by_id(session, coin_id)
        logger.info(f"Coin with id {coin_id} retrieved successfully")
        return coin


@app.put(
    "/coins/{coin_id}",
    response_model=CoinBase,
    responses={404: {"description": "Coin not found"}},
)
async def update_coin(coin_id: str, coin: CoinUpdate):
    async with db_connection.async_session() as session:
        existing_coin: SQLAlchemyCoin = await get_coin_by_id(session, coin_id)
        # Update coin data using CoinUpdateService
        updated_coin_data: CoinUpdate = await coin_update_service.update_coin_data(
            coin_id, coin
        )
        update_data = updated_coin_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_coin, key, value)
        await session.commit()
        await session.refresh(existing_coin)
        logger.info(f"Coin with id {coin_id} updated successfully")
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
        logger.info(f"Coin with id {coin_id} deleted successfully")
    return {"message": "Coin deleted successfully"}


@app.get("/coins/", response_model=list[CoinBase])
async def list_coins():
    async with db_connection.async_session() as session:
        result = await session.execute(select(SQLAlchemyCoin))
        coins = result.scalars().all()
        logger.info("List of coins retrieved successfully")
        return coins


@app.post(
    "/update-coins/", responses={200: {"description": "Coin data update triggered"}}
)
async def trigger_coin_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(periodic_updater.fetch_and_cache_coin_data)
    logger.info("Manual coin data update triggered")
    return {"message": "Coin data update triggered"}
