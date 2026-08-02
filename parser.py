"""
parser.py
---------
Transforms raw OpenWeatherMap JSON payloads into clean Python data structures.

This module deliberately has **no side-effects** — it never performs network
requests and never writes to files.  Every public function accepts a plain
``dict`` and returns a typed value, making the module fully unit-testable
without mocking.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from exceptions import ParsingError
from logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

WeatherData = dict[str, Any]
"""Parsed, application-ready weather data dictionary."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _safe_get(data: dict[str, Any], *keys: str, default: Any = "N/A") -> Any:
    """
    Safely traverse nested dictionary keys, returning *default* on any miss.

    Parameters
    ----------
    data:
        The dictionary to traverse.
    *keys:
        An ordered sequence of dictionary keys forming the path.
    default:
        Value returned when any key in the path is missing.

    Returns
    -------
    Any
        The value found at the end of the key path, or *default*.
    """
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


def convert_time(unix_timestamp: int, timezone_offset: int) -> str:
    """
    Convert a UNIX timestamp to a human-readable local time string.

    The OpenWeatherMap API returns timestamps in UTC.  The ``timezone``
    field in the response is the shift from UTC in **seconds** (not hours),
    which is applied here to produce the city's local time.

    Parameters
    ----------
    unix_timestamp:
        Seconds since the UNIX epoch (UTC).
    timezone_offset:
        City-local UTC offset in seconds.

    Returns
    -------
    str
        Formatted time string, e.g. ``"06:42 AM"``.

    Example
    -------
    >>> convert_time(1700000000, 19800)
    '11:53 AM'
    """
    try:
        utc_dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
        local_dt = utc_dt + timedelta(seconds=timezone_offset)
        return local_dt.strftime("%b %d, %I:%M %p")
    except (OSError, OverflowError, ValueError) as exc:
        log.warning("Failed to convert timestamp %s: %s", unix_timestamp, exc)
        return "N/A"


def weather_icon(condition_id: int) -> str:
    """
    Map an OpenWeatherMap weather condition ID to a representative emoji.

    Condition ID ranges are documented at:
    https://openweathermap.org/weather-conditions

    Parameters
    ----------
    condition_id:
        Integer weather condition code returned by the API.

    Returns
    -------
    str
        A single emoji character representing the weather condition.

    Example
    -------
    >>> weather_icon(800)
    '☀️'
    >>> weather_icon(500)
    '🌧️'
    """
    if condition_id in range(200, 300):
        return "⛈️"   # Thunderstorm
    if condition_id in range(300, 400):
        return "🌦️"   # Drizzle
    if condition_id in range(500, 600):
        return "🌧️"   # Rain
    if condition_id in range(600, 700):
        return "❄️"   # Snow
    if condition_id in range(700, 800):
        return "🌫️"   # Atmosphere (fog, mist, haze…)
    if condition_id == 800:
        return "☀️"   # Clear sky
    if condition_id in range(801, 900):
        return "☁️"   # Clouds
    return "🌤️"       # Fallback


def wind_direction(degrees: float) -> str:
    """
    Convert wind bearing in degrees to a cardinal/intercardinal direction.

    Parameters
    ----------
    degrees:
        Wind direction in meteorological degrees (0 = North, clockwise).

    Returns
    -------
    str
        A cardinal or intercardinal label such as ``"N"``, ``"NE"``, etc.

    Example
    -------
    >>> wind_direction(45)
    'NE'
    >>> wind_direction(180)
    'S'
    """
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    index = int((degrees + 11.25) / 22.5) % 16
    return directions[index]


def parse_weather(raw: dict[str, Any]) -> WeatherData:
    """
    Parse a raw OpenWeatherMap ``/data/2.5/weather`` response into a flat dict.

    Parameters
    ----------
    raw:
        The decoded JSON payload from the API response.

    Returns
    -------
    WeatherData
        A flat dictionary with human-readable keys and formatted values
        ready for display.

    Raises
    ------
    ParsingError
        If the payload is not a dictionary or critical fields are absent.

    Example
    -------
    >>> data = parse_weather(raw_json_dict)
    >>> data["city"]
    'London'
    """
    if not isinstance(raw, dict):
        raise ParsingError(
            message="Unexpected API response format.",
            details=f"Expected a JSON object, got {type(raw).__name__}.",
        )

    # Validate mandatory top-level keys.
    required_keys = {"main", "weather", "wind", "sys", "name"}
    missing = required_keys - raw.keys()
    if missing:
        log.error("API response is missing required keys: %s", missing)
        raise ParsingError(
            message="Incomplete data received from the API.",
            details=f"Missing keys: {', '.join(sorted(missing))}",
        )

    try:
        timezone_offset: int = _safe_get(raw, "timezone", default=0)
        condition_list: list[dict[str, Any]] = raw.get("weather", [{}])
        condition: dict[str, Any] = condition_list[0] if condition_list else {}
        condition_id: int = condition.get("id", 0)

        wind_deg: float = float(_safe_get(raw, "wind", "deg", default=0.0))
        visibility_m: float = float(_safe_get(raw, "visibility", default=0.0))
        # Convert visibility from metres to kilometres, clamped between 0 and 10 km.
        visibility_km: float = max(0.0, min(visibility_m / 1000.0, 10.0))

        parsed: WeatherData = {
            # Location
            "city": _safe_get(raw, "name"),
            "country": _safe_get(raw, "sys", "country"),
            # Temperature (°C in metric mode)
            "temperature": _safe_get(raw, "main", "temp"),
            "feels_like": _safe_get(raw, "main", "feels_like"),
            "temp_min": _safe_get(raw, "main", "temp_min"),
            "temp_max": _safe_get(raw, "main", "temp_max"),
            # Atmosphere
            "humidity": _safe_get(raw, "main", "humidity"),
            "pressure": _safe_get(raw, "main", "pressure"),
            "visibility_km": round(visibility_km, 1),
            # Wind
            "wind_speed": _safe_get(raw, "wind", "speed"),
            "wind_direction": wind_direction(float(wind_deg)),
            # Condition
            "condition": condition.get("main", "N/A"),
            "description": (
                desc.capitalize()
                if (desc := condition.get("description", "N/A")) != "N/A"
                else "N/A"
            ),
            "condition_id": condition_id,
            "icon": weather_icon(condition_id),
            # Time
            "sunrise": convert_time(
                _safe_get(raw, "sys", "sunrise", default=0),
                timezone_offset,
            ),
            "sunset": convert_time(
                _safe_get(raw, "sys", "sunset", default=0),
                timezone_offset,
            ),
            "timezone_offset": timezone_offset,
            "last_updated": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            # Coordinates
            "latitude": _safe_get(raw, "coord", "lat"),
            "longitude": _safe_get(raw, "coord", "lon"),
        }

        log.debug("Parsed weather data for '%s'.", parsed["city"])
        return parsed

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        log.exception("Unexpected error while parsing API response.")
        raise ParsingError(
            message="Failed to parse weather data.",
            details=str(exc),
        ) from exc
