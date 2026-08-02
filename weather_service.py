"""
weather_service.py
------------------
Network layer for the Weather Information App.

Responsible exclusively for making HTTP requests to the OpenWeatherMap API
and returning the raw JSON payload.  All business logic and presentation
concerns are handled by ``parser.py`` and ``display.py`` respectively.
"""

from __future__ import annotations

from typing import Any

import requests
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
)
from requests.exceptions import (
    JSONDecodeError,
    Timeout,
)

import config
from exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    ParsingError,
    RateLimitError,
    WeatherAPIError,
)
from exceptions import (
    NetworkError as AppConnectionError,
)
from logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

_CITY_MIN_LENGTH: int = 2
_CITY_MAX_LENGTH: int = 100


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def validate_city(city: str) -> str:
    """
    Sanitise and validate a city name entered by the user.

    The function strips surrounding whitespace, enforces length bounds, and
    rejects input that consists solely of digits or punctuation symbols.

    Parameters
    ----------
    city:
        Raw city string from user input.

    Returns
    -------
    str
        The stripped, validated city name.

    Raises
    ------
    ValueError
        With a descriptive message if the city name fails any validation rule.

    Example
    -------
    >>> validate_city("  London  ")
    'London'
    >>> validate_city("123")
    ValueError: City name must not be numbers only.
    """
    stripped: str = city.strip()

    if not stripped:
        raise ValueError("City name must not be blank.")

    if stripped.isdigit():
        raise ValueError("City name must not be numbers only.")

    if not any(c.isalpha() for c in stripped):
        raise ValueError("City name must contain at least one letter (cannot be symbols only).")

    if len(stripped) < _CITY_MIN_LENGTH:
        raise ValueError(
            f"City name is too short (minimum {_CITY_MIN_LENGTH} characters)."
        )

    if len(stripped) > _CITY_MAX_LENGTH:
        raise ValueError(
            f"City name is too long (maximum {_CITY_MAX_LENGTH} characters)."
        )

    log.debug("City name validated: '%s'", stripped)
    return stripped


# ---------------------------------------------------------------------------
# API request
# ---------------------------------------------------------------------------


def fetch_weather(city: str, api_key: str) -> dict[str, Any]:
    """
    Request current weather data for *city* from the OpenWeatherMap API.

    Parameters
    ----------
    city:
        A validated city name to look up.
    api_key:
        A non-empty OpenWeatherMap API key.

    Returns
    -------
    dict[str, Any]
        The decoded JSON response body.

    Raises
    ------
    InvalidAPIKeyError
        HTTP 401 — the API key is invalid or revoked.
    CityNotFoundError
        HTTP 404 — no city matches the requested name.
    RateLimitError
        HTTP 429 — the account has exceeded its request quota.
    WeatherAPIError
        Any other non-200 HTTP response.
    AppConnectionError
        A network-level failure (DNS, timeout, refused connection, etc.).
    ParsingError
        The response body cannot be decoded as JSON.

    Example
    -------
    >>> raw = fetch_weather("London", api_key)
    >>> raw["name"]
    'London'
    """
    params: dict[str, str] = {
        "q": city,
        "appid": api_key,
        "units": config.UNITS,
    }

    log.info("Fetching weather data for city='%s'.", city)

    try:
        response = requests.get(
            url=config.BASE_URL,
            params=params,
            timeout=config.REQUEST_TIMEOUT,
        )
    except Timeout:
        log.error("Request timed out after %ds for city='%s'.", config.REQUEST_TIMEOUT, city)
        raise AppConnectionError(
            message="The request timed out.",
            details=(
                f"No response received within {config.REQUEST_TIMEOUT} seconds. "
                "Check your internet connection and try again."
            ),
        )
    except RequestsConnectionError as exc:
        log.error("Network error while fetching weather for '%s': %s", city, exc)
        raise AppConnectionError(
            message="Unable to connect to the weather service.",
            details="Please check your internet connection and try again.",
        ) from exc

    # ------------------------------------------------------------------
    # HTTP error dispatch
    # ------------------------------------------------------------------
    status: int = response.status_code

    if status == config.HTTP_OK:
        try:
            payload: dict[str, Any] = response.json()
            log.info(
                "Successfully fetched weather data for '%s' (HTTP %d).", city, status
            )
            return payload
        except (JSONDecodeError, ValueError) as exc:
            log.error("Failed to decode JSON response for '%s': %s", city, exc)
            raise ParsingError(
                message="Received an invalid response from the weather service.",
                details="The response body could not be parsed as JSON.",
            ) from exc

    if status == config.HTTP_UNAUTHORIZED:
        log.error("Invalid API key used for request (HTTP 401).")
        raise InvalidAPIKeyError(
            message="Your API key is invalid or has been revoked.",
            details=(
                "Verify that WEATHER_API_KEY in your .env file is correct and "
                "that the key is active on openweathermap.org."
            ),
        )

    if status == config.HTTP_NOT_FOUND:
        log.warning("City not found: '%s' (HTTP 404).", city)
        raise CityNotFoundError(
            message=f"City '{city}' was not found.",
            details=(
                "Double-check the spelling or try a nearby larger city. "
                "Country codes can be appended for disambiguation, e.g. 'London,GB'."
            ),
        )

    if status == config.HTTP_TOO_MANY_REQUESTS:
        log.warning("API rate limit exceeded (HTTP 429).")
        raise RateLimitError(
            message="API rate limit exceeded.",
            details=(
                "You have exceeded your OpenWeatherMap request quota. "
                "Wait a minute before trying again, or upgrade your plan."
            ),
        )

    if status >= config.HTTP_INTERNAL_SERVER_ERROR:
        log.error("OpenWeatherMap server error (HTTP %d).", status)
        raise WeatherAPIError(
            message="The weather service is currently unavailable.",
            status_code=status,
            details=f"Server responded with HTTP {status}. Please try again later.",
        )

    # Catch-all for unexpected status codes.
    log.error("Unexpected HTTP status %d for city='%s'.", status, city)
    raise WeatherAPIError(
        message="Received an unexpected response from the weather service.",
        status_code=status,
        details=f"HTTP {status}: {response.text[:200]}",
    )
