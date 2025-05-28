from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.config import settings
from src.prisma_client import Prisma

logger = getLogger(__name__)
prisma = Prisma()


@asynccontextmanager
async def get_db() -> AsyncGenerator[Prisma, None]:
    """
    Yield a connected Prisma client. Assumes init_db() has already connected.
    """
    if not prisma.is_connected():
        logger.warning("Prisma was disconnected; reconnecting.")
        await prisma.connect()

    try:
        yield prisma
    except Exception as e:
        logger.error(f"Database query error: {str(e)}", exc_info=True)
        raise


async def init_db() -> None:
    try:
        if not prisma.is_connected():
            logger.info("Connecting to the database...")
            await prisma.connect()
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        raise


async def close_db() -> None:
    try:
        if prisma.is_connected():
            logger.info("Disconnecting database...")
            await prisma.disconnect()
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}", exc_info=True)
        raise


async def init_redis_cache() -> None:
    """
    Initialize Redis cache for FastAPI.
    """
    redis_client = redis.Redis(
        host=settings.HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    await init_redis_cache()
    yield
    await close_db()
