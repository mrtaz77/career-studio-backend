from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from fastapi import FastAPI

from src.prisma_client import Prisma

logger = getLogger(__name__)
db = Prisma()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Connecting to the database...")
    await db.connect()
    logger.info("Database connection established.")

    try:
        yield
    finally:
        logger.info("Disconnecting from the database...")
        await db.disconnect()
        logger.info("Database connection closed.")
