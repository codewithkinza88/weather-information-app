# 🌤️ Weather Information App

> A cinematic CLI weather experience that turns raw OpenWeatherMap data into a polished, story-driven terminal dashboard.

<div align="center">

**Built to feel like a product, not a script.**

Fast validation. Clean architecture. Rich-rendered weather output that looks intentional from the first run.

</div>

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Rich Framework](https://img.shields.io/badge/Rich-Terminal%20UI-red?style=for-the-badge&logo=terminal&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-149%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

## Why it feels exceptional

- It does not just print weather data. It stages it like a finished product.
- The flow is calm, fast, and deliberate: validate, fetch, parse, render, repeat.
- Rich panels and structured layouts give the app a premium terminal identity.
- The code is split into clean modules, so the design feels engineered rather than improvised.

## At a glance

| Signal | Detail |
| :-- | :-- |
| Core experience | Interactive city weather lookup in the terminal |
| Rendering engine | Rich-powered cards, tables, and polished output |
| Reliability | Defensive validation and custom exceptions |
| Architecture | Modular, test-friendly, single-responsibility design |
| Quality bar | 149 tests, offline-safe validation, structured logs |

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Security & Logging](#security--logging)
- [Roadmap](#roadmap)
- [License](#license)
- [Author](#author)

## Overview

The **Weather Information App** is a Python 3.10+ CLI dashboard for checking live weather data by city name. It uses the [OpenWeatherMap Current Weather API](https://openweathermap.org/current), transforms the response into structured data, and renders the result through [Rich](https://github.com/Textualize/rich) with a presentation-first terminal layout.

The app is designed around separation of concerns, so network calls, parsing, display logic, and validation stay isolated, testable, and easy to evolve.

## Key Features

| Category | What it delivers |
| :-- | :-- |
| 🌡️ Weather intelligence | Live temperature, feels-like, min/max, humidity, pressure, and visibility data. |
| 🌬️ Wind intelligence | Wind speed plus automatic degree-to-direction translation. |
| 🌅 Solar timing | Sunrise and sunset rendered in the target city's local timezone. |
| 📍 Location context | City, country, latitude, and longitude in one readable view. |
| 🎨 Premium terminal UI | Rich panels, tables, and color treatment that feel intentionally designed. |
| 🛡️ Guardrails | Rejects invalid input before it can reach the API layer. |
| 🚦 Logging discipline | Rotating logs preserve issues without cluttering the terminal. |

## Tech Stack

- Python 3.10+
- Requests
- Rich
- python-dotenv
- Pytest
- Ruff
- MyPy

## How It Works

```text
User enters a city
        |
        v
validate_city()
        |
   valid? yes -------------------------------> fetch_weather()
        |                                           |
        no                                          v
        |                                    parse_weather()
        v                                           |
Styled error panel                           display_weather()
                                                    |
                                                    v
                                           prompt for another city
```

## What reviewers notice first

1. The output looks polished the moment the app starts.
2. The error handling feels professional instead of noisy.
3. The folder layout makes the project easy to understand quickly.
4. The tests show the app was built with discipline, not just demo energy.

## Project Structure

```text
weather-information-app/
├── weather_app.py        # Main entry point and application loop
├── weather_service.py    # API communication and validation
├── parser.py             # OpenWeatherMap response parsing
├── display.py            # Rich terminal rendering
├── config.py             # Configuration and environment loading
├── exceptions.py         # Custom exception hierarchy
├── logger.py             # Rotating logging setup
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── CHANGELOG.md          # Release notes
├── LICENSE               # MIT license
└── tests/                # Offline test suite
    ├── test_api.py
    ├── test_parser.py
    ├── test_display.py
    └── test_validation.py
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/codewithkinza88/weather-information-app.git
cd weather-information-app
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python weather_app.py
```

## Configuration

1. Copy the example environment file.

```bash
copy .env.example .env
```

2. Add your API key.

```dotenv
WEATHER_API_KEY=your_secured_openweathermap_api_key_here
```

> [!IMPORTANT]
> Keep real API keys out of public commits. The repository is set up to keep `.env` values out of version control.

## Usage

Launch the app with:

```bash
python weather_app.py
```

You can then enter a city name such as `Rome`, `New York`, `Mumbai`, or `Tokyo`. The app prints a polished weather card, then asks whether you want to search again.

Press `Ctrl + C` or `Ctrl + D` to exit gracefully.

## Error Handling

The app avoids raw stack traces in normal use. Instead, it maps failures to explicit domain-level responses.

| Error State | Raised Exception | User-facing result |
| :-- | :-- | :-- |
| Missing configuration | `APIKeyMissingError` | Explains that the API key is not configured. |
| Invalid API key | `InvalidAPIKeyError` | Prompts the user to verify the OpenWeatherMap key. |
| City not found | `CityNotFoundError` | Tells the user the city could not be resolved. |
| Network failure | `ConnectionError` | Reports that the API could not be reached. |
| Timeout | `ConnectionError` | Explains the server did not respond in time. |
| Rate limit | `RateLimitError` | Indicates too many requests were sent. |
| Parsing failure | `ParsingError` | Signals that the API response was incomplete or invalid. |

## Testing

The repository includes **149 test cases** covering API handling, parsing, display formatting, and validation logic.

```bash
pytest tests/ -v
```

For coverage:

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

## Security & Logging

- API credentials are loaded from environment variables, not hard-coded.
- Runtime logs are stored locally in rotating files under `logs/`.
- Validation happens before external requests, reducing bad calls and noisy failures.

## Roadmap

- Add a 5-day forecast view.
- Surface Air Quality Index data.
- Add export options for CSV or JSON reports.
- Improve search flow with fuzzy autocompletion.
- Expand unit support options.

## License

Distributed under the [MIT License](LICENSE).

## Author

**Kinza Kareem**

Crafted with a focus on clarity, presentation, and real-world usability.

- GitHub: https://github.com/codewithkinza88
- LinkedIn: https://github.com/codewithkinza88/weather-information-app.git

<div align="center">

If this project impressed you, star it and keep building on the idea.

</div>

