from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from fastapi import FastAPI

from src.prisma_client import Prisma

logger = getLogger(__name__)

# Global Prisma client instance
prisma = Prisma()


@asynccontextmanager
async def get_db() -> AsyncGenerator[Prisma, None]:
    """
    Async context manager for database operations.
    Ensures proper connection and disconnection of the Prisma client.
    """
    try:
        if not prisma.is_connected():
            logger.debug("Connecting to database...")
            await prisma.connect()
        yield prisma
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}", exc_info=True)
        raise
    finally:
        if prisma.is_connected():
            logger.debug("Disconnecting from database...")
            await prisma.disconnect()


async def init_db() -> None:
    """Initialize database connection."""
    try:
        if not prisma.is_connected():
            logger.info("Initializing database connection...")
            await prisma.connect()
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise


async def close_db() -> None:
    """Close database connection."""
    try:
        if prisma.is_connected():
            logger.info("Closing database connection...")
            await prisma.disconnect()
    except Exception as e:
        logger.error(f"Failed to close database connection: {str(e)}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Connecting to the database...")
    await prisma.connect()
    logger.info("Database connection established.")

    try:
        yield
    finally:
        logger.info("Disconnecting from the database...")
        await prisma.disconnect()
        logger.info("Database connection closed.")
