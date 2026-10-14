"""
Central logging configuration.

Every module should import get_logger()
instead of creating its own logger.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from configs.settings import settings


# ---------------------------------------------------------
# Log Format
# ---------------------------------------------------------

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ---------------------------------------------------------
# Configure Root Logger
# ---------------------------------------------------------

def setup_logging() -> None:
    """
    Configure console and file logging.

    Safe to call multiple times.
    """

    log_dir: Path = settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "hybridrag.log"

    root_logger = logging.getLogger()

    # Avoid duplicate handlers if called twice
    if root_logger.handlers:
        return

    root_logger.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter(
        LOG_FORMAT,
        DATE_FORMAT
    )

    # ----------------------------------
    # Console Handler
    # ----------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # ----------------------------------
    # File Handler
    # ----------------------------------

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,   # 10 MB
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)


# ---------------------------------------------------------
# Public Logger
# ---------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Example
    -------
    logger = get_logger(__name__)
    """

    setup_logging()

    return logging.getLogger(name)