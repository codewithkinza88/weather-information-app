"""
config.py
---------
Application-wide configuration and environment management.

Reads the ``WEATHER_API_KEY`` from the environment (optionally loaded from a
``.env`` file via *python-dotenv*) and exposes every API-related constant
used throughout the project.  Importing this module is the single source of
truth for tunable parameters.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from exceptions import APIKeyMissingError
from logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Load .env — safe to call multiple times; subsequent calls are no-ops.
# ---------------------------------------------------------------------------
_ENV_PATH: Path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)

# ---------------------------------------------------------------------------
# OpenWeatherMap API configuration
# ---------------------------------------------------------------------------

BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
"""Full URL for the Current Weather Data endpoint."""

UNITS: str = "metric"
"""
Unit system passed to the API.

* ``metric``   — temperature in °C, wind speed in m/s
* ``imperial`` — temperature in °F, wind speed in mph
* ``standard`` — temperature in Kelvin, wind speed in m/s
"""

# Labels derived from UNITS so display.py never hard-codes them.
_TEMP_LABELS: dict[str, str] = {
    "metric": "°C",
    "imperial": "°F",
    "standard": "K",
}
_SPEED_LABELS: dict[str, str] = {
    "metric": "m/s",
    "imperial": "mph",
    "standard": "m/s",
}
TEMP_UNIT: str = _TEMP_LABELS.get(UNITS, "°C")
"""Temperature unit label matching the active UNITS setting."""
SPEED_UNIT: str = _SPEED_LABELS.get(UNITS, "m/s")
"""Wind speed unit label matching the active UNITS setting."""

REQUEST_TIMEOUT: int = 10
"""Maximum number of seconds to wait for an API response."""

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------

APP_NAME: str = "Weather Information App"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Weather App"

# ---------------------------------------------------------------------------
# HTTP status codes used in error handling
# ---------------------------------------------------------------------------

HTTP_OK: int = 200
HTTP_UNAUTHORIZED: int = 401
HTTP_NOT_FOUND: int = 404
HTTP_TOO_MANY_REQUESTS: int = 429
HTTP_INTERNAL_SERVER_ERROR: int = 500


def load_api_key() -> str:
    """
    Load and return the OpenWeatherMap API key from the environment.

    The function reads ``WEATHER_API_KEY`` after *python-dotenv* has
    already attempted to populate the environment from ``.env``.

    Returns
    -------
    str
        The non-empty API key string.

    Raises
    ------
    APIKeyMissingError
        If ``WEATHER_API_KEY`` is absent or blank.

    Example
    -------
    >>> from config import load_api_key
    >>> api_key = load_api_key()
    """
    api_key: str | None = os.getenv("WEATHER_API_KEY", "").strip()

    if not api_key:
        log.error("WEATHER_API_KEY is missing or empty in the environment.")
        raise APIKeyMissingError(
            message="API key not found.",
            details=(
                "Set WEATHER_API_KEY in your .env file or as an environment variable. "
                "See .env.example for reference."
            ),
        )

    log.debug("API key loaded successfully.")
    return api_key
