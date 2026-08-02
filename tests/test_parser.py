"""
tests/test_parser.py
--------------------
Unit tests for ``parser.py``.

All tests are fully offline — no network calls are made.  The test suite
verifies:

* Successful parsing of a realistic API payload.
* Correct extraction of every field exposed by ``parse_weather()``.
* Correct behaviour of ``convert_time()``.
* Correct emoji mapping in ``weather_icon()``.
* Correct cardinal-direction mapping in ``wind_direction()``.
* Graceful degradation when optional fields are missing.
* ``ParsingError`` raised on invalid input types.
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Make the project root importable when running pytest from any directory.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from exceptions import ParsingError
from parser import (
    _safe_get,
    convert_time,
    parse_weather,
    weather_icon,
    wind_direction,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_raw_payload() -> dict:
    """Return a realistic OpenWeatherMap JSON payload for London."""
    return {
        "coord": {"lon": -0.1257, "lat": 51.5085},
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d",
            }
        ],
        "base": "stations",
        "main": {
            "temp": 18.5,
            "feels_like": 17.9,
            "temp_min": 15.2,
            "temp_max": 21.3,
            "pressure": 1015,
            "humidity": 62,
        },
        "visibility": 10000,
        "wind": {"speed": 4.1, "deg": 230},
        "clouds": {"all": 0},
        "dt": 1700000000,
        "sys": {
            "type": 2,
            "id": 2075535,
            "country": "GB",
            "sunrise": 1699940452,
            "sunset": 1699974521,
        },
        "timezone": 0,
        "id": 2643743,
        "name": "London",
        "cod": 200,
    }


# ---------------------------------------------------------------------------
# Tests: parse_weather — happy path
# ---------------------------------------------------------------------------


class TestParseWeatherHappyPath:
    """parse_weather() correctly extracts all fields from a valid payload."""

    def test_city_name(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["city"] == "London"

    def test_country(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["country"] == "GB"

    def test_temperature(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["temperature"] == 18.5

    def test_feels_like(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["feels_like"] == 17.9

    def test_temp_min(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["temp_min"] == 15.2

    def test_temp_max(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["temp_max"] == 21.3

    def test_humidity(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["humidity"] == 62

    def test_pressure(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["pressure"] == 1015

    def test_visibility_capped_at_10km(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["visibility_km"] == 10.0

    def test_wind_speed(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["wind_speed"] == 4.1

    def test_wind_direction(self, sample_raw_payload):
        # 230° → SSW
        data = parse_weather(sample_raw_payload)
        assert data["wind_direction"] == "SW"

    def test_condition(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["condition"] == "Clear"

    def test_description_capitalised(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["description"] == "Clear sky"

    def test_condition_id(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["condition_id"] == 800

    def test_icon_clear_sky(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["icon"] == "☀️"

    def test_latitude(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["latitude"] == 51.5085

    def test_longitude(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["longitude"] == -0.1257

    def test_last_updated_present(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["last_updated"] != "N/A"
        assert len(data["last_updated"]) > 0

    def test_sunrise_present(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["sunrise"] != "N/A"

    def test_sunset_present(self, sample_raw_payload):
        data = parse_weather(sample_raw_payload)
        assert data["sunset"] != "N/A"


# ---------------------------------------------------------------------------
# Tests: parse_weather — error paths
# ---------------------------------------------------------------------------


class TestParseWeatherErrors:
    """parse_weather() raises ParsingError on invalid input."""

    def test_raises_on_list_input(self):
        with pytest.raises(ParsingError, match="Unexpected API response format"):
            parse_weather([])  # type: ignore[arg-type]

    def test_raises_on_string_input(self):
        with pytest.raises(ParsingError):
            parse_weather("not a dict")  # type: ignore[arg-type]

    def test_raises_on_none_input(self):
        with pytest.raises(ParsingError):
            parse_weather(None)  # type: ignore[arg-type]

    def test_raises_on_missing_main(self, sample_raw_payload):
        del sample_raw_payload["main"]
        with pytest.raises(ParsingError, match="Incomplete data"):
            parse_weather(sample_raw_payload)

    def test_raises_on_missing_weather(self, sample_raw_payload):
        del sample_raw_payload["weather"]
        with pytest.raises(ParsingError, match="Incomplete data"):
            parse_weather(sample_raw_payload)

    def test_raises_on_missing_sys(self, sample_raw_payload):
        del sample_raw_payload["sys"]
        with pytest.raises(ParsingError, match="Incomplete data"):
            parse_weather(sample_raw_payload)


# ---------------------------------------------------------------------------
# Tests: parse_weather — edge cases
# ---------------------------------------------------------------------------


class TestParseWeatherEdgeCases:
    """parse_weather() handles unusual but valid data gracefully."""

    def test_visibility_below_10km(self, sample_raw_payload):
        sample_raw_payload["visibility"] = 5000
        data = parse_weather(sample_raw_payload)
        assert data["visibility_km"] == 5.0

    def test_visibility_zero(self, sample_raw_payload):
        sample_raw_payload["visibility"] = 0
        data = parse_weather(sample_raw_payload)
        assert data["visibility_km"] == 0.0

    def test_empty_weather_list_uses_defaults(self, sample_raw_payload):
        sample_raw_payload["weather"] = []
        data = parse_weather(sample_raw_payload)
        assert data["condition"] == "N/A"
        assert data["description"] == "N/A"

    def test_negative_timezone_offset(self, sample_raw_payload):
        sample_raw_payload["timezone"] = -18000  # UTC-5 (New York)
        data = parse_weather(sample_raw_payload)
        assert data["timezone_offset"] == -18000

    def test_unicode_city_name(self, sample_raw_payload):
        sample_raw_payload["name"] = "São Paulo"
        data = parse_weather(sample_raw_payload)
        assert data["city"] == "São Paulo"


# ---------------------------------------------------------------------------
# Tests: convert_time
# ---------------------------------------------------------------------------


class TestConvertTime:
    """convert_time() converts UNIX timestamps to readable local time strings."""

    def test_returns_string(self):
        result = convert_time(1700000000, 0)
        assert isinstance(result, str)

    def test_format_am_pm(self):
        # 1700000000 UTC = 2023-11-14 22:13:20 UTC → 10:13 PM
        result = convert_time(1700000000, 0)
        assert "AM" in result or "PM" in result

    def test_positive_offset_applied(self):
        # UTC+5:30 = +19800 seconds
        utc_result = convert_time(1700000000, 0)
        ist_result = convert_time(1700000000, 19800)
        assert utc_result != ist_result

    def test_invalid_timestamp_returns_na(self):
        result = convert_time(-99999999999, 0)
        assert result == "N/A"

    def test_zero_timestamp(self):
        result = convert_time(0, 0)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Tests: weather_icon
# ---------------------------------------------------------------------------


class TestWeatherIcon:
    """weather_icon() maps condition IDs to the correct emoji."""

    def test_thunderstorm_200(self):
        assert weather_icon(200) == "⛈️"

    def test_thunderstorm_299(self):
        assert weather_icon(299) == "⛈️"

    def test_drizzle_300(self):
        assert weather_icon(300) == "🌦️"

    def test_rain_500(self):
        assert weather_icon(500) == "🌧️"

    def test_snow_600(self):
        assert weather_icon(600) == "❄️"

    def test_atmosphere_701(self):
        assert weather_icon(701) == "🌫️"

    def test_clear_800(self):
        assert weather_icon(800) == "☀️"

    def test_clouds_801(self):
        assert weather_icon(801) == "☁️"

    def test_clouds_804(self):
        assert weather_icon(804) == "☁️"

    def test_unknown_id_fallback(self):
        assert weather_icon(999) == "🌤️"

    def test_zero_id_fallback(self):
        assert weather_icon(0) == "🌤️"


# ---------------------------------------------------------------------------
# Tests: wind_direction
# ---------------------------------------------------------------------------


class TestWindDirection:
    """wind_direction() converts degrees to cardinal abbreviations."""

    def test_north_0(self):
        assert wind_direction(0) == "N"

    def test_north_360(self):
        assert wind_direction(360) == "N"

    def test_north_east_45(self):
        assert wind_direction(45) == "NE"

    def test_east_90(self):
        assert wind_direction(90) == "E"

    def test_south_180(self):
        assert wind_direction(180) == "S"

    def test_west_270(self):
        assert wind_direction(270) == "W"

    def test_south_south_west_225(self):
        assert wind_direction(225) == "SW"

    def test_north_north_east_22(self):
        assert wind_direction(22) == "NNE"


# ---------------------------------------------------------------------------
# Tests: _safe_get
# ---------------------------------------------------------------------------


class TestSafeGet:
    """_safe_get() handles nested dictionary traversal safely."""

    def test_single_key(self):
        assert _safe_get({"a": 1}, "a") == 1

    def test_nested_key(self):
        assert _safe_get({"a": {"b": 2}}, "a", "b") == 2

    def test_missing_key_returns_default(self):
        assert _safe_get({"a": 1}, "b") == "N/A"

    def test_custom_default(self):
        assert _safe_get({}, "x", default=0) == 0

    def test_non_dict_intermediate_returns_default(self):
        assert _safe_get({"a": "string"}, "a", "b") == "N/A"

    def test_empty_dict(self):
        assert _safe_get({}, "key") == "N/A"

    def test_explicit_none_returns_default(self):
        assert _safe_get({"a": None}, "a") == "N/A"
        assert _safe_get({"a": None}, "a", default=0.0) == 0.0
