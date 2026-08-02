"""
weather_app.py
--------------
Entry point for the Weather Information App.

This module wires together every other module — configuration loading,
input validation, API fetching, JSON parsing, and Rich display — into the
main application loop.  It is the only module that contains orchestration
logic.  Import from sibling modules freely; never re-implement functionality
that already exists in them.

Usage
-----
    python weather_app.py

Or, if installed as a script entry-point:

    weather-app
"""

from __future__ import annotations

import sys

import config
import display
from exceptions import (
    APIKeyMissingError,
    CityNotFoundError,
    InvalidAPIKeyError,
    ParsingError,
    RateLimitError,
    WeatherAPIError,
    WeatherAppError,
)
from exceptions import (
    NetworkError as AppConnectionError,
)
from logger import get_logger
from parser import parse_weather
from weather_service import fetch_weather, validate_city

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Application loop
# ---------------------------------------------------------------------------


def _run_search_cycle(api_key: str) -> None:
    """
    Execute one complete city-search cycle: prompt → validate → fetch → display.

    Parameters
    ----------
    api_key:
        A pre-validated OpenWeatherMap API key.

    Raises
    ------
    Any exception raised by the underlying modules is caught and displayed as
    a styled error panel; the function then returns normally so the caller can
    decide whether to repeat.
    """
    raw_input: str = display.prompt_city()

    # Validate city name.
    try:
        city = validate_city(raw_input)
    except ValueError as exc:
        display.display_error("Invalid City Name", str(exc))
        log.warning("City validation failed: %s", exc)
        return

    display.display_info(f"Fetching weather for [bold]{city}[/bold] …")

    # Fetch raw JSON from the API.
    try:
        raw_data = fetch_weather(city, api_key)
    except CityNotFoundError as exc:
        display.display_error("City Not Found 🗺", exc.message, exc.details)
        return
    except InvalidAPIKeyError as exc:
        display.display_error("Invalid API Key 🔑", exc.message, exc.details)
        return
    except RateLimitError as exc:
        display.display_error("Rate Limit Exceeded ⏳", exc.message, exc.details)
        return
    except AppConnectionError as exc:
        display.display_error("Connection Error 🌐", exc.message, exc.details)
        return
    except WeatherAPIError as exc:
        display.display_error(
            f"API Error (HTTP {exc.status_code})", exc.message, exc.details
        )
        return

    # Parse the JSON payload.
    try:
        weather_data = parse_weather(raw_data)
    except ParsingError as exc:
        display.display_error("Parsing Error", exc.message, exc.details)
        return

    # Render the dashboard.
    display.display_weather(weather_data)


def main() -> None:
    """
    Application entry point.

    Sets up the terminal UI, loads the API key, then drives the interactive
    search loop until the user chooses to exit.  All unrecoverable errors
    (missing API key, unexpected exceptions) are displayed gracefully and
    cause the process to exit with a non-zero status code.
    """
    display.display_welcome_banner()

    # ------------------------------------------------------------------
    # Load the API key — abort immediately if it is missing.
    # ------------------------------------------------------------------
    try:
        api_key = config.load_api_key()
    except APIKeyMissingError as exc:
        display.display_error("API Key Missing 🔑", exc.message, exc.details)
        log.critical("Application cannot start without an API key.")
        sys.exit(1)

    log.info("Weather Information App started (v%s).", config.APP_VERSION)

    # ------------------------------------------------------------------
    # Interactive search loop.
    # ------------------------------------------------------------------
    while True:
        try:
            _run_search_cycle(api_key)
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C / Ctrl+D during a prompt — exit the loop gracefully.
            break
        except WeatherAppError as exc:
            # Catch any app-level exception that leaked out of _run_search_cycle.
            display.display_error("Unexpected Error", exc.message, exc.details)
            log.exception("Unhandled WeatherAppError reached main().")
        except Exception:
            # Absolute last resort — never show a traceback to the user.
            display.display_error(
                "Unexpected Error",
                "An unexpected internal error occurred.",
                "The error has been logged. Please try again.",
            )
            log.exception("Unhandled exception in main loop.")
            break

        try:
            if not display.prompt_continue():
                break
        except (KeyboardInterrupt, EOFError):
            break

    display.display_goodbye()
    log.info("Weather Information App exited normally.")


# ---------------------------------------------------------------------------
# Script entry-point guard
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
