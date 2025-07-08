from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from supabase import Client, create_client

from src.config import settings
from src.prisma_client import Prisma
from src.prisma_client.errors import PrismaError

logger = getLogger(__name__)
prisma = Prisma()
supabase: Client


@asynccontextmanager
async def get_db() -> AsyncGenerator[Prisma, None]:
    """
    Yield a connected Prisma client. Assumes init_db() has already connected.
    """
    await init_db()

    try:
        yield prisma
    except PrismaError as e:  # Only catch DB-specific exceptions
        logger.error(f"Database query error: {e}")
        raise


async def init_db() -> None:
    try:
        if not prisma.is_connected():
            await prisma.connect()
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        raise


async def close_db() -> None:
    """
    Close the database connection safely.
    """
    try:
        if prisma.is_connected():
            await prisma.disconnect()
            logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error disconnecting from database: {e}", exc_info=True)
        # Don't re-raise during cleanup - just log the error


def init_redis_cache() -> None:
    """
    Initialize Redis cache for FastAPI.
    """
    redis_client = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")


@asynccontextmanager
async def get_supabase() -> AsyncGenerator[Client, None]:
    if supabase is None:
        await init_supabase()

    try:
        yield supabase
    except Exception as e:
        logger.error(f"Supabase client error: {str(e)}", exc_info=True)
        raise


def init_supabase() -> None:
    global supabase
    try:
        supabase_project_url = settings.SUPABASE_PROJECT_URL
        supabase_service_role_key = settings.SUPABASE_SERVICE_ROLE_KEY

        supabase = create_client(supabase_project_url, supabase_service_role_key)

    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Handles startup and shutdown of database and cache connections.
    """
    try:
        # Startup
        await init_db()
        init_redis_cache()
        init_supabase()
        logger.info("Application startup complete")
        yield
    finally:
        # Shutdown - ensure cleanup happens even if there are errors
        try:
            await close_db()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}", exc_info=True)
