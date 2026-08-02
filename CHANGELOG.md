# Changelog

All notable changes to **Weather Information App** are documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- 5-day / 3-hour forecast support via the `/forecast` endpoint.
- City search history stored in a local SQLite database.
- Air Quality Index (AQI) data from the OpenWeatherMap Air Pollution API.
- Optional export of results to JSON or CSV.
- Interactive city autocomplete using fuzzy matching.

---

## [1.0.0] — 2024-01-15

### Added
- **Core application** (`weather_app.py`) with an interactive search loop, graceful
  `KeyboardInterrupt` / `EOFError` handling, and a clean goodbye screen.
- **Network layer** (`weather_service.py`) using `requests` with a configurable
  timeout and full HTTP-error dispatch (401, 404, 429, 5xx).
- **Parser module** (`parser.py`) that converts raw OpenWeatherMap JSON into a
  flat, typed `WeatherData` dictionary with no side effects.
- **Rich terminal UI** (`display.py`) featuring:
  - Animated welcome banner with app version.
  - Location header panel with coordinates and last-updated time.
  - Condition strip displaying icon, description, temperature, and feels-like.
  - Two-column metrics table covering atmosphere, wind, and astronomical data.
  - Styled error, info, success, and goodbye panels.
- **Configuration module** (`config.py`) as the single source of truth for API
  settings, loaded via `python-dotenv`.
- **Custom exception hierarchy** (`exceptions.py`) with six specialised exception
  classes covering every anticipated failure mode.
- **Centralised logging** (`logger.py`) using a rotating file handler
  (`logs/weather.log`, 5 MB per file, 3 backups) and a WARNING-level console
  handler.
- **Input validation** in `weather_service.validate_city()` with rules for blank,
  numbers-only, symbols-only, length bounds, and illegal characters.
- **Full pytest suite** (`tests/`) with 80+ test cases covering:
  - `test_parser.py` — parsing, helper functions, edge cases.
  - `test_validation.py` — all validation rules and boundary conditions.
  - `test_api.py` — mocked HTTP responses for all status codes and network errors.
  - `test_display.py` — Rich console output captured via StringIO.
- **Documentation** — `README.md` with badges, architecture diagram, data-flow
  diagram, installation guide, usage instructions, and contribution guidelines.
- **Project scaffolding** — `.gitignore`, `.env.example`, `LICENSE` (MIT),
  `requirements.txt`, and `screenshots/` placeholder directory.

### Security
- API key read exclusively from the `WEATHER_API_KEY` environment variable.
- `.env` file excluded from version control via `.gitignore`.
- `.env.example` provided as a safe template with a placeholder value (no real credentials).

---

[Unreleased]: https://github.com/your-username/weather-information-app/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/weather-information-app/releases/tag/v1.0.0
