import logging

from colorlog import ColoredFormatter


def setup_logging() -> None:
    """Configure logging using colorlog."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # default for all

    # Clean up old handlers to prevent duplicates
    _clear_existing_handlers(root)

    handler = _create_stream_handler()
    root.addHandler(handler)

    # Set specific log levels for external libraries
    _set_library_log_levels()


def _clear_existing_handlers(logger: logging.Logger) -> None:
    """Remove existing handlers from the logger."""
    if logger.hasHandlers():
        logger.handlers.clear()


def _create_stream_handler() -> logging.Handler:
    """Create and configure a stream handler with a colored formatter."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s:     [%(name)s] (%(filename)s:%(lineno)d) %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)
    return handler


def _set_library_log_levels() -> None:
    """Set specific log levels for external libraries."""
    for logger_name in ["httpcore", "httpx", "src.prisma_client"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


setup_logging()
