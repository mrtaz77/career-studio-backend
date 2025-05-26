from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from fastapi import FastAPI

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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield
    await close_db()
