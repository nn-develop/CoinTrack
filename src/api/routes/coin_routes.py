from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.coin import Coin as SQLAlchemyCoin
from src.schemas.coin import CoinBase, CoinCreate, CoinUpdate
from src.services.coin_update_service import CoinUpdateService
from src.logger import logger
from src.services.periodic_coin_data_updater import PeriodicCoinDataUpdater
from src.services.coin_service import CoinService
from src.dependencies import get_db

router = APIRouter(prefix="/coins", tags=["coins"])
coin_update_service = CoinUpdateService()
periodic_updater = PeriodicCoinDataUpdater()


@router.post(
    "/",
    response_model=CoinBase,
    status_code=status.HTTP_201_CREATED,
    responses={201: {"description": "Coin created successfully"}},
)
async def create_coin(coin: CoinCreate, session: AsyncSession = Depends(get_db)):
    await CoinService.handle_coin_already_exists(session, coin.id)
    try:
        updated_coin_data: CoinUpdate = await coin_update_service.update_coin_data(coin)
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
        raise HTTPException(status_code=400, detail="Coin with this ID already exists")


@router.get(
    "/{coin_id}",
    response_model=CoinBase,
    responses={404: {"description": "Coin not found"}},
)
async def get_coin(coin_id: str, session: AsyncSession = Depends(get_db)):
    coin = await CoinService.handle_coin_not_found(session, coin_id)
    logger.info(f"Coin with id {coin_id} retrieved successfully")
    return coin


@router.put(
    "/{coin_id}",
    response_model=CoinBase,
    responses={404: {"description": "Coin not found"}},
)
async def update_coin(
    coin_id: str, coin: CoinUpdate, session: AsyncSession = Depends(get_db)
):
    if not coin.id:
        coin.id = coin_id
    if coin_id != coin.id:
        raise HTTPException(
            status_code=400,
            detail="Coin ID mismatch. Coin ID in URL must match Coin ID in request body",
        )

    existing_coin: SQLAlchemyCoin = await CoinService.handle_coin_not_found(
        session, coin.id
    )
    updated_coin_data: CoinUpdate = await coin_update_service.update_coin_data(coin)
    update_data = updated_coin_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_coin, key, value)
    await session.commit()
    await session.refresh(existing_coin)
    logger.info(f"Coin with id {coin_id} updated successfully")
    return existing_coin


@router.delete(
    "/{coin_id}",
    responses={
        404: {"description": "Coin not found"},
        200: {"description": "Coin deleted successfully"},
    },
)
async def delete_coin(coin_id: str, session: AsyncSession = Depends(get_db)):
    coin = await CoinService.handle_coin_not_found(session, coin_id)
    await session.delete(coin)
    await session.commit()
    logger.info(f"Coin with id {coin_id} deleted successfully")
    return {"message": "Coin deleted successfully"}


@router.get("/", response_model=list[CoinBase])
async def list_coins(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(SQLAlchemyCoin))
    coins = result.scalars().all()
    logger.info("List of coins retrieved successfully")
    return coins


@router.post(
    "/update-coins/", responses={200: {"description": "Coin data update triggered"}}
)
async def trigger_coin_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(periodic_updater.fetch_and_cache_coin_data)
    logger.info("Manual coin data update triggered")
    return {"message": "Coin data update triggered"}
