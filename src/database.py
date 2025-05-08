from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from src.generated.prisma import Prisma

logger = getLogger(__name__)
db = Prisma()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Connecting to the database...")
    await db.connect()
    logger.info("Database connection established.")

    try:
        yield
    finally:
        logger.info("Disconnecting from the database...")
        await db.disconnect()
        logger.info("Database connection closed.")
