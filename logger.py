"""
logger.py
---------
Centralised logging configuration for the Weather Information App.

Creates a rotating-file handler that writes structured log records to
``logs/weather.log`` and a console handler that emits WARNING-and-above
messages to stderr.  All application modules obtain their logger via the
``get_logger()`` factory so configuration is applied exactly once.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Anchor the log directory to the project root (directory of this file).
# Using a relative path would scatter log files wherever the command is run.
_PROJECT_ROOT: Path = Path(__file__).parent
LOG_DIR: Path = _PROJECT_ROOT / "logs"
LOG_FILE: Path = LOG_DIR / "weather.log"
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
MAX_BYTES: int = 5 * 1024 * 1024   # 5 MB per file
BACKUP_COUNT: int = 3              # keep up to 3 rotated files


def _configure_root_logger() -> None:
    """
    Set up the root logger with a rotating file handler and a stderr handler.

    This function is idempotent — subsequent calls will not add duplicate
    handlers because the guard ``if root.handlers`` short-circuits.
    """
    root: logging.Logger = logging.getLogger()

    # Guard against duplicate configuration: check whether *our* file handler
    # has already been attached. This avoids being fooled by handlers that
    # pytest or third-party libraries may have added to the root logger.
    if any(
        isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == str(LOG_FILE.resolve())
        for h in root.handlers
    ):
        return

    root.setLevel(logging.DEBUG)

    # -----------------------------------------------------------------------
    # Ensure the log directory exists before creating the file handler.
    # -----------------------------------------------------------------------
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # File handler — DEBUG and above, rotated at 5 MB, keeping 3 archives.
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler — WARNING and above so the terminal stays uncluttered.
    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger after ensuring the root logger is configured.

    Parameters
    ----------
    name:
        Typically ``__name__`` of the calling module.

    Returns
    -------
    logging.Logger
        A child logger of the configured root logger.

    Example
    -------
    >>> from logger import get_logger
    >>> log = get_logger(__name__)
    >>> log.info("Application started.")
    """
    _configure_root_logger()
    return logging.getLogger(name)
