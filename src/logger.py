import logging
import logging.config

from src.config import settings


def setup_logging() -> None:
    """Configure logging using logging.ini with color support."""
    logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

    if settings.ENVIRONMENT != "development":
        # Suppress noisy uvicorn logs in production
        logging.getLogger("uvicorn").propagate = False
        logging.getLogger("uvicorn.access").disabled = True


setup_logging()
logger = logging.getLogger(__name__)
