"""
tests/test_api.py
-----------------
Unit tests for ``weather_service.fetch_weather()``.

All HTTP calls are intercepted and mocked using ``unittest.mock.patch`` so
these tests run entirely offline.  The test suite covers:

* Successful 200 responses.
* HTTP 401 → InvalidAPIKeyError.
* HTTP 404 → CityNotFoundError.
* HTTP 429 → RateLimitError.
* HTTP 500 → WeatherAPIError.
* Network timeouts → AppConnectionError.
* DNS / connection failures → AppConnectionError.
* Invalid JSON bodies → ParsingError.
* Unexpected non-standard status codes → WeatherAPIError.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch

import pytest
import requests

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
from weather_service import fetch_weather

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_API_KEY = "fake_test_api_key_1234567890"
SAMPLE_CITY = "London"

SAMPLE_RESPONSE_BODY = {
    "coord": {"lon": -0.1257, "lat": 51.5085},
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
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
    "sys": {"country": "GB", "sunrise": 1699940452, "sunset": 1699974521},
    "timezone": 0,
    "name": "London",
    "cod": 200,
}


def _make_mock_response(status_code: int, body: dict | str | None = None) -> MagicMock:
    """
    Create a MagicMock that mimics a ``requests.Response``.

    Parameters
    ----------
    status_code:
        The HTTP status code to return.
    body:
        Dictionary to be returned by ``.json()``, or a raw string for the
        ``.text`` attribute.  If ``None``, ``.json()`` raises ``ValueError``.
    """
    mock = MagicMock()
    mock.status_code = status_code

    if isinstance(body, dict):
        mock.json.return_value = body
        mock.text = json.dumps(body)
    elif isinstance(body, str):
        mock.text = body
        mock.json.side_effect = ValueError("No JSON object could be decoded")
    else:
        mock.json.side_effect = ValueError("No JSON object could be decoded")
        mock.text = ""

    return mock


# ---------------------------------------------------------------------------
# Tests: successful responses
# ---------------------------------------------------------------------------


class TestFetchWeatherSuccess:
    """fetch_weather() returns the decoded payload on HTTP 200."""

    @patch("weather_service.requests.get")
    def test_returns_dict_on_200(self, mock_get):
        mock_get.return_value = _make_mock_response(200, SAMPLE_RESPONSE_BODY)
        result = fetch_weather(SAMPLE_CITY, FAKE_API_KEY)
        assert isinstance(result, dict)

    @patch("weather_service.requests.get")
    def test_city_name_in_result(self, mock_get):
        mock_get.return_value = _make_mock_response(200, SAMPLE_RESPONSE_BODY)
        result = fetch_weather(SAMPLE_CITY, FAKE_API_KEY)
        assert result["name"] == "London"

    @patch("weather_service.requests.get")
    def test_correct_params_passed(self, mock_get):
        mock_get.return_value = _make_mock_response(200, SAMPLE_RESPONSE_BODY)
        fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

        call_kwargs = mock_get.call_args[1]
        params = call_kwargs["params"]
        assert params["q"] == SAMPLE_CITY
        assert params["appid"] == FAKE_API_KEY
        assert params["units"] == "metric"

    @patch("weather_service.requests.get")
    def test_timeout_is_set(self, mock_get):
        mock_get.return_value = _make_mock_response(200, SAMPLE_RESPONSE_BODY)
        fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

        call_kwargs = mock_get.call_args[1]
        assert "timeout" in call_kwargs
        assert call_kwargs["timeout"] > 0


# ---------------------------------------------------------------------------
# Tests: HTTP error responses
# ---------------------------------------------------------------------------


class TestFetchWeatherHTTPErrors:
    """fetch_weather() raises the correct custom exception for each HTTP error."""

    @patch("weather_service.requests.get")
    def test_401_raises_invalid_api_key(self, mock_get):
        mock_get.return_value = _make_mock_response(401)
        with pytest.raises(InvalidAPIKeyError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

    @patch("weather_service.requests.get")
    def test_404_raises_city_not_found(self, mock_get):
        mock_get.return_value = _make_mock_response(404)
        with pytest.raises(CityNotFoundError):
            fetch_weather("NonExistentCityXYZ", FAKE_API_KEY)

    @patch("weather_service.requests.get")
    def test_404_error_message_contains_city(self, mock_get):
        mock_get.return_value = _make_mock_response(404)
        with pytest.raises(CityNotFoundError) as exc_info:
            fetch_weather("NonExistentCityXYZ", FAKE_API_KEY)
        assert "NonExistentCityXYZ" in str(exc_info.value)

    @patch("weather_service.requests.get")
    def test_429_raises_rate_limit(self, mock_get):
        mock_get.return_value = _make_mock_response(429)
        with pytest.raises(RateLimitError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

    @patch("weather_service.requests.get")
    def test_500_raises_weather_api_error(self, mock_get):
        mock_get.return_value = _make_mock_response(500)
        with pytest.raises(WeatherAPIError) as exc_info:
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)
        assert exc_info.value.status_code == 500

    @patch("weather_service.requests.get")
    def test_503_raises_weather_api_error(self, mock_get):
        mock_get.return_value = _make_mock_response(503)
        with pytest.raises(WeatherAPIError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

    @patch("weather_service.requests.get")
    def test_unexpected_status_raises_weather_api_error(self, mock_get):
        mock_get.return_value = _make_mock_response(418)  # I'm a teapot
        with pytest.raises(WeatherAPIError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)


# ---------------------------------------------------------------------------
# Tests: network errors
# ---------------------------------------------------------------------------


class TestFetchWeatherNetworkErrors:
    """fetch_weather() raises AppConnectionError on network failures."""

    @patch("weather_service.requests.get")
    def test_timeout_raises_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(AppConnectionError, match="timed out"):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

    @patch("weather_service.requests.get")
    def test_connection_refused_raises_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        with pytest.raises(AppConnectionError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)

    @patch("weather_service.requests.get")
    def test_dns_failure_raises_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno -2] Name or service not known"
        )
        with pytest.raises(AppConnectionError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)


# ---------------------------------------------------------------------------
# Tests: invalid JSON response
# ---------------------------------------------------------------------------


class TestFetchWeatherInvalidJSON:
    """fetch_weather() raises ParsingError when the 200 body is invalid JSON."""

    @patch("weather_service.requests.get")
    def test_invalid_json_on_200_raises_parsing_error(self, mock_get):
        mock_get.return_value = _make_mock_response(200, "not valid json at all")
        with pytest.raises(ParsingError):
            fetch_weather(SAMPLE_CITY, FAKE_API_KEY)
