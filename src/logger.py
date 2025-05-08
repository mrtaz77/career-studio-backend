import logging
from colorlog import ColoredFormatter

def setup_logging() -> None:
    """Configure logging using colorlog."""
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
        }
    )

    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # default for all

    # Clean up old handlers to prevent duplicates
    root.handlers.clear()
    root.addHandler(handler)

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("src.generated").setLevel(logging.WARNING)

setup_logging()