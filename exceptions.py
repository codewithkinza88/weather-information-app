"""
exceptions.py
-------------
Custom exception hierarchy for the Weather Information App.

All application-specific exceptions inherit from WeatherAppError,
enabling clean, granular error handling throughout the codebase.
"""


class WeatherAppError(Exception):
    """
    Base exception for the Weather Information App.

    All custom exceptions inherit from this class, allowing callers
    to catch any application-level error with a single except clause.
    """

    def __init__(self, message: str, details: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} — {self.details}"
        return self.message


class APIKeyMissingError(WeatherAppError):
    """
    Raised when the WEATHER_API_KEY environment variable is absent or empty.

    This typically occurs when the user has not created a .env file or has
    forgotten to populate it with a valid OpenWeatherMap API key.
    """


class InvalidAPIKeyError(WeatherAppError):
    """
    Raised when the OpenWeatherMap API responds with HTTP 401 Unauthorized.

    This indicates the provided API key is malformed, revoked, or invalid.
    """


class CityNotFoundError(WeatherAppError):
    """
    Raised when the OpenWeatherMap API responds with HTTP 404 Not Found.

    This indicates the requested city name does not match any known location
    in the OpenWeatherMap database.
    """


class WeatherAPIError(WeatherAppError):
    """
    Raised for unexpected HTTP error codes returned by the API.

    Captures the HTTP status code alongside a human-readable message so
    that callers can log or display context-specific information.
    """

    def __init__(self, message: str, status_code: int = 0, details: str = "") -> None:
        super().__init__(message, details)
        self.status_code = status_code


class NetworkError(WeatherAppError):
    """
    Raised when a network-level failure prevents reaching the API.

    Covers scenarios such as DNS resolution failures, refused connections,
    and request timeouts.
    """


class RateLimitError(WeatherAppError):
    """
    Raised when the OpenWeatherMap API responds with HTTP 429 Too Many Requests.

    The free-tier API key is subject to 60 calls/minute and 1 000 000 calls/month.
    """


class ParsingError(WeatherAppError):
    """
    Raised when the API response cannot be decoded or expected fields are absent.

    This usually indicates a breaking change in the API response schema or an
    unexpectedly malformed payload.
    """
