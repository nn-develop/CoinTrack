from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database_utils.connection import DatabaseConnection
from src.redis_cache.redis_cache import RedisCache
from src.logger import logger

router = APIRouter(prefix="/health", tags=["health"])


async def get_db():
    """Database session dependency"""
    db_connection = DatabaseConnection()
    async with db_connection.async_session() as session:
        yield session


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint that returns 200 OK if the service is running
    """
    return {"status": "ok", "service": "cointrack-api"}


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(session: AsyncSession = Depends(get_db)):
    """
    Readiness check that verifies database and Redis connections are working
    """
    health_status = {
        "status": "ok",
        "database": False,
        "redis": False,
    }

    # Check database connection
    try:
        await session.execute("SELECT 1")
        health_status["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        redis_cache = RedisCache()
        redis_cache.client.ping()
        health_status["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["status"] = "degraded"

    if health_status["status"] != "ok":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not fully operational",
        )

    return health_status


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check that simply returns 200 OK to indicate the service is alive
    Used by container orchestration systems like Kubernetes
    """
    return {"status": "alive"}


@router.get("/version", status_code=status.HTTP_200_OK)
async def version_info():
    """
    Returns version information about the API
    """
    return {
        "version": "1.0.0",
        "api": "CoinTrack API",
    }
