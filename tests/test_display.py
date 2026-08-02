"""
tests/test_display.py
---------------------
Unit tests for ``display.py``.

Because display functions write to a Rich Console, tests capture output
by redirecting the shared console to a StringIO buffer.  No visual
assertions are made about styling; we assert on the *content* of the
rendered text and on the call signatures of interactive prompt helpers.

Covered functions:
* display_welcome_banner()
* display_weather()
* display_error()
* display_info()
* display_success()
* display_goodbye()
* _format_timezone()
* _fmt_temp(), _fmt_speed(), _fmt_pressure(), _fmt_humidity(), _fmt_visibility()
"""

from __future__ import annotations

import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch

from rich.console import Console

import display as display_module
from display import (
    _fmt_humidity,
    _fmt_pressure,
    _fmt_speed,
    _fmt_temp,
    _fmt_visibility,
    _format_timezone,
    display_error,
    display_goodbye,
    display_info,
    display_success,
    display_weather,
    display_welcome_banner,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _capture(func, *args, **kwargs) -> str:
    """
    Execute *func* with a Rich Console that writes to a StringIO buffer.

    Returns the captured plain-text output (no ANSI codes).
    """
    buf = io.StringIO()
    test_console = Console(file=buf, no_color=True, highlight=False, width=120)
    with patch.object(display_module, "console", test_console):
        func(*args, **kwargs)
    return buf.getvalue()


SAMPLE_WEATHER_DATA = {
    "city": "Tokyo",
    "country": "JP",
    "latitude": 35.6895,
    "longitude": 139.6917,
    "temperature": 22.4,
    "feels_like": 21.8,
    "temp_min": 19.0,
    "temp_max": 25.6,
    "humidity": 74,
    "pressure": 1012,
    "visibility_km": 8.5,
    "wind_speed": 3.6,
    "wind_direction": "NE",
    "condition": "Clouds",
    "description": "Broken clouds",
    "condition_id": 803,
    "icon": "☁️",
    "sunrise": "06:12 AM",
    "sunset": "06:47 PM",
    "timezone_offset": 32400,
    "last_updated": "2024-01-15 10:30:00",
}


# ---------------------------------------------------------------------------
# Tests: display_welcome_banner
# ---------------------------------------------------------------------------


class TestDisplayWelcomeBanner:
    """display_welcome_banner() renders the app name and version."""

    def test_contains_app_name(self):
        output = _capture(display_welcome_banner)
        assert "Weather Information App" in output

    def test_contains_version(self):
        output = _capture(display_welcome_banner)
        assert "1.0.0" in output

    def test_contains_openweathermap_reference(self):
        output = _capture(display_welcome_banner)
        assert "OpenWeatherMap" in output


# ---------------------------------------------------------------------------
# Tests: display_weather
# ---------------------------------------------------------------------------


class TestDisplayWeather:
    """display_weather() renders all expected weather fields."""

    def test_city_name_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "Tokyo" in output

    def test_country_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "JP" in output

    def test_temperature_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "22.4" in output

    def test_humidity_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "74" in output

    def test_wind_speed_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "3.6" in output

    def test_wind_direction_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "NE" in output

    def test_description_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "Broken clouds" in output

    def test_sunrise_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "06:12 AM" in output

    def test_sunset_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "06:47 PM" in output

    def test_pressure_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "1012" in output

    def test_visibility_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "8.5" in output

    def test_last_updated_shown(self):
        output = _capture(display_weather, SAMPLE_WEATHER_DATA)
        assert "2024-01-15" in output


# ---------------------------------------------------------------------------
# Tests: display_error
# ---------------------------------------------------------------------------


class TestDisplayError:
    """display_error() renders title, message, and optional details."""

    def test_title_shown(self):
        output = _capture(display_error, "City Not Found", "Tokyo was not found.")
        assert "City Not Found" in output

    def test_message_shown(self):
        output = _capture(display_error, "City Not Found", "Tokyo was not found.")
        assert "Tokyo was not found." in output

    def test_details_shown_when_provided(self):
        output = _capture(
            display_error,
            "Error Title",
            "Main message.",
            "Some extra detail here.",
        )
        assert "Some extra detail here." in output

    def test_no_exception_raised(self):
        # Should complete without raising.
        _capture(display_error, "Test", "No crash please.")


# ---------------------------------------------------------------------------
# Tests: display_info and display_success
# ---------------------------------------------------------------------------


class TestDisplayInfoSuccess:
    """display_info() and display_success() render their messages."""

    def test_display_info_contains_message(self):
        output = _capture(display_info, "Loading weather data…")
        assert "Loading weather data" in output

    def test_display_success_contains_message(self):
        output = _capture(display_success, "Data fetched successfully.")
        assert "Data fetched successfully." in output


# ---------------------------------------------------------------------------
# Tests: display_goodbye
# ---------------------------------------------------------------------------


class TestDisplayGoodbye:
    """display_goodbye() renders a farewell message."""

    def test_contains_app_name(self):
        output = _capture(display_goodbye)
        assert "Weather Information App" in output


# ---------------------------------------------------------------------------
# Tests: _format_timezone
# ---------------------------------------------------------------------------


class TestFormatTimezone:
    """_format_timezone() converts UTC offset seconds to readable strings."""

    def test_utc_zero(self):
        assert _format_timezone(0) == "UTC+0:00"

    def test_positive_full_hour(self):
        assert _format_timezone(3600) == "UTC+1:00"

    def test_positive_half_hour(self):
        assert _format_timezone(19800) == "UTC+5:30"

    def test_negative_full_hour(self):
        assert _format_timezone(-18000) == "UTC-5:00"

    def test_negative_half_hour(self):
        assert _format_timezone(-9000) == "UTC-2:30"

    def test_positive_nine_hours(self):
        # Japan Standard Time
        assert _format_timezone(32400) == "UTC+9:00"


# ---------------------------------------------------------------------------
# Tests: formatting helpers
# ---------------------------------------------------------------------------


class TestFormattingHelpers:
    """_fmt_* helpers produce correctly formatted strings."""

    # _fmt_temp
    def test_fmt_temp_normal(self):
        assert _fmt_temp(22.4) == "22.4 °C"

    def test_fmt_temp_na(self):
        assert _fmt_temp("N/A") == "N/A"

    def test_fmt_temp_negative(self):
        assert _fmt_temp(-5.0) == "-5.0 °C"

    def test_fmt_temp_zero(self):
        assert _fmt_temp(0) == "0.0 °C"

    # _fmt_speed
    def test_fmt_speed_normal(self):
        assert _fmt_speed(3.6) == "3.6 m/s"

    def test_fmt_speed_na(self):
        assert _fmt_speed("N/A") == "N/A"

    # _fmt_pressure
    def test_fmt_pressure_normal(self):
        assert _fmt_pressure(1012) == "1012 hPa"

    def test_fmt_pressure_na(self):
        assert _fmt_pressure("N/A") == "N/A"

    # _fmt_humidity
    def test_fmt_humidity_normal(self):
        assert _fmt_humidity(74) == "74 %"

    def test_fmt_humidity_na(self):
        assert _fmt_humidity("N/A") == "N/A"

    # _fmt_visibility
    def test_fmt_visibility_normal(self):
        assert _fmt_visibility(8.5) == "8.5 km"

    def test_fmt_visibility_na(self):
        assert _fmt_visibility("N/A") == "N/A"
