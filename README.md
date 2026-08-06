# 🌤️ Weather Information App

**A modern command-line interface weather dashboard powered by OpenWeatherMap and rendered with Rich.**

---

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Rich Framework](https://img.shields.io/badge/Rich-Terminal%20UI-red?style=for-the-badge&logo=terminal&logoColor=white)](https://github.com/Textualize/rich)
[![Testing Coverage](https://img.shields.io/badge/Tests-149%20Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 📖 Table of Contents
]
- [Overview](#-overview)
- [Technologies Used](#-technologies-used)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Application Data Flow](#-application-data-flow)
- [Detailed Module Guide](#-detailed-module-guide)
- [Project Directory Structure](#-project-directory-structure)
- [Installation Guide](#-installation-guide)
- [Configuration & Environment](#-configuration--environment)
- [Usage & Console Experience](#-usage--console-experience)
- [Example Output](#-example-output)
- [Error Handling Framework](#-error-handling-framework)
- [Testing & Validation Suite](#-testing--validation-suite)
- [Security & Logging Standards](#-security--logging-standards)
- [Future Roadmap](#-future-roadmap)
- [License](#-license)

---

## 🌍 Overview

The **Weather Information App** is a polished Command-Line Interface (CLI) application that delivers real-time weather analytics for cities globally. Built with Python 3.10+, it provides an interactive terminal dashboard. 

The application utilizes a clean separation-of-concerns pattern to query the [OpenWeatherMap Current Weather API](https://openweathermap.org/current), parse JSON payloads into structured data models, validate inputs, and present an optimized UI using the [Rich](https://github.com/Textualize/rich) library.

---

## 🛠 Technologies Used

- Python 3.10+
- Requests
- Rich
- python-dotenv
- Pytest
- Ruff
- MyPy

---

## ✨ Key Features

| Category | High-End Feature Highlights |
| :--- | :--- |
| 🌡️ **Weather Analytics** | Computes current, feels-like, minimum, and maximum temperatures; relative humidity, barometric pressure, and outdoor visibility distance. |
| 🌬️ **Wind Metrics** | Identifies wind speeds (m/s) and automatically maps degrees to standard cardinal compass directions (e.g., N, NE, SSW). |
| 🌅 **Astronomical Details** | Calculates and displays exact local sunrise/sunset times adjusted dynamically to the target city's timezone. |
| 📍 **Geolocation Context** | Details precise latitude, longitude coordinates, and country indicators for search queries. |
| 🎨 **Terminal UI Engine** | Employs Rich panels, sub-tables, color gradients, micro-symbol indicators, and border layouts for a seamless dark-theme terminal experience. |
| 🛡️ **Input Validation** | Implements pre-flight input sanitization to catch empty, numeric, excessively long, or invalid Unicode queries before calling external APIs. |
| 🚦 **Error & Activity Logging** | Features a rotating file logger keeping up to 5MB logs across multiple generations to maintain zero terminal clutter. |

---

## 🏗️ System Architecture

The project is structured around a strict modular design, dividing core behaviors into separate packages to make testing and maintenance painless:

```
┌─────────────────────────────────────────────────────────┐
│                    weather_app.py                       │
│              (Orchestration / Entry Point)               │
│                    Main App Controller                  │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    [ Network Layer ] [ Parse Layer ] [ UI Render ]
    weather_service.py   parser.py       display.py
           │
           ▼
    ┌──────────────┐
    │ OpenWeather  │
    │ Map API v2.5 │
    └──────────────┘

  ┌────────────────────────────────────────────────────────┐
  │ Shared Utilities: exceptions.py, config.py, logger.py  │
  └────────────────────────────────────────────────────────┘
```

### Module Responsibilities

1. **[weather_app.py](weather_app.py)**: The central controller managing the runtime lifecycle, interactive input loops, and overall exception routing.
2. **[weather_service.py](weather_service.py)**: Manages network requests, custom API headers, HTTP error dispatching, and user-input validation rules.
3. **[parser.py](parser.py)**: A stateless utility that parses dynamic JSON dictionaries into a typed, structured `WeatherData` object.
4. **[display.py](display.py)**: Houses formatting methods, panel styling, color layouts, and interactive terminal prompts.
5. **[config.py](config.py)**: Central source of truth for global constants, path helpers, and API credentials loaded safely from environment files.
6. **[exceptions.py](exceptions.py)**: Implements custom domain exception types.
7. **[logger.py](logger.py)**: Sets up professional logging streams to rotatable local logfiles.

---

## 🔄 Application Data Flow

```
[ User Inputs City Query ]
            │
            ▼
┌─────────────────────────┐
│  validate_city()        │  (Validates blank, length, Unicode symbols)
└───────────┬─────────────┘
            │  Invalid Input
            ├─────────────────────────────────► [ Display Styled Error Panel ]
            │  Valid Input
            ▼
┌─────────────────────────┐
│  fetch_weather()        │  (Initiates API request using Requests library)
└───────────┬─────────────┘
            │  HTTP Error / Network Outage
            ├─────────────────────────────────► [ Parse & Map Custom Exceptions ]
            │  HTTP 200 OK                                   │
            ▼                                                ▼
┌─────────────────────────┐                      [ Render Error Dashboard ]
│  parse_weather()        │
└───────────┬─────────────┘
            │  JSON Parsing Failure
            ├─────────────────────────────────► [ Raise ParsingError ]
            │  Success Mapping
            ▼
┌─────────────────────────┐
│  display_weather()      │  (Compiles Rich Columns, Panels, and Tables)
└───────────┬─────────────┘
            │
            ▼
[ Prompt: Search Again? ] ◄──── Loop or Exit Gracefully
```

## 🔍 Detailed Module Guide

Each script in the application has a singular, dedicated responsibility:

* **[weather_app.py](weather_app.py)**: The main entry point. Houses the main loop, coordinates data transitions between modules, handles unhandled exceptions gracefully, and prints the startup banner.
* **[weather_service.py](weather_service.py)**: The remote communicator. Uses the `requests` library to fetch current weather details. Provides city name input validation (blocking empty, numeric, or excessively long/corrupt strings).
* **[parser.py](parser.py)**: The raw data transformer. Converts the raw nested OpenWeatherMap API JSON response dictionary into a flat, typed data structure. Automatically maps wind angles to cardinal directions and timestamp integers to formatted local time strings.
* **[display.py](display.py)**: The console renderer. Contains Rich layout specifications, color parameters, grids, panels, horizontal rules, and terminal prompts. Completely decoupled from network or disk operations for effortless testing.
* **[config.py](config.py)**: Configuration repository. Loads environment details (via `python-dotenv`), manages fallback options, sets request timeouts, and defines standard temperature and speed unit designations.
* **[exceptions.py](exceptions.py)**: Custom domain exceptions framework. Extends from a base `WeatherAppError` to capture precise API, network, rate limits, parsing, or setup errors.
* **[logger.py](logger.py)**: The telemetry framework. Implements file logging via a `RotatingFileHandler` with 5MB maximum space and three backup files, keeping runtime errors logged without polluting user terminals.

---

## 📁 Project Directory Structure

```
weather-information-app/
│
├── weather_app.py        # Central runtime loop & main entry point
├── weather_service.py    # Remote HTTP network wrapper & validation
├── parser.py             # Pure functional data parser
├── display.py            # Rich terminal layout and interface configurations
├── config.py             # Application settings & environment handling
├── exceptions.py         # Specialized error hierarchy
├── logger.py             # Rotating log handling configurations
│
├── requirements.txt      # Pin-point project dependencies
├── README.md             # Project documentation (This file)
├── LICENSE               # MIT License metadata
├── CHANGELOG.md          # Version details & changes
├── .gitignore            # Version control exclusions
├── .env.example          # Sample environment layout (safe for distribution)
│
└── tests/                # Complete test framework suite
    ├── __init__.py
    ├── test_api.py        # Simulated API responses & HTTP test scenarios
    ├── test_parser.py     # Pure data unit tests
    ├── test_display.py    # Captured terminal layout validation
    └── test_validation.py # Verification of city input validation rules
```

---

## 🚀 Installation Guide

### System Prerequisites
* **Python 3.10+** (Confirm using `python --version`)
* **pip** (Python package installer)
* A valid **OpenWeatherMap API Key** (Obtainable from [OpenWeatherMap Portal](https://home.openweathermap.org/users/sign_up))

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/codewithkinza88/weather-information-app.git
   cd weather-information-app
   ```

2. **Configure Virtual Environment**
   ```bash
   # Initialize environment
   python -m venv venv

   # Activate on Windows (PowerShell/CMD)
   .\venv\Scripts\activate

   # Activate on macOS / Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Configuration & Environment

1. Make a copy of the environment template:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` in your editor and enter your private API token:
   ```dotenv
   WEATHER_API_KEY=your_secured_openweathermap_api_key_here
   ```

> [!IMPORTANT]
> Keep your real API key out of public commits. The `.gitignore` file is pre-configured to prevent `.env` files from leaking into version control.

---

## 💻 Usage & Console Experience

Start the interactive terminal CLI dashboard:
```bash
python weather_app.py
```

### Experience Workflow:
1. **Dynamic Welcome**: A clean header panel welcoming you to the app is printed.
2. **Interactive Search Prompt**: Enter the city name (e.g., `Rome`, `New York`, `Mumbai`, `Tokyo`).
3. **Responsive Render**: A custom-formatted, double-column weather block displays local values.
4. **Interactive Repeat Loop**: Prompted to lookup another city or type `n` to exit cleanly.

### Navigation Shortcuts
* `Ctrl + C` or `Ctrl + D` triggers a graceful shutdown sequence and closes the application instantly without producing Python stacktraces.

---

## 📊 Example Output

When running in your console, the terminal renders formatted output resembling this:

```
╭─────────────────────────────────────────────────────────╮
│        🌤️  Weather Information App  🌤️                   │
│  v1.0.0  •  Real-time weather powered by OpenWeatherMap  │
│                                                         │
│  Type 'exit' or press Ctrl+C to terminate at any time.  │
╰─────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────╮
│          📍 London, GB                                   │
│  🛰️  51.5085°N  -0.1257°E   •   🕐 Updated: 10:30:00    │
╰─────────────────────────────────────────────────────────╯

╭──────────────── ☁️  Clouds ────────────────╮
│              ☁️  overcast clouds            │
│        14.8 °C   Feels like  14.2 °C     │
│     Low 13.0 °C   •   High  16.0 °C      │
╰──────────────────────────────────────────╯

╭─── 🌡️ Atmosphere ───╮  ╭─── 🌬️ Wind & Sun ───╮
│ Temperature  14.8°C │  │ Wind Speed  2.5 m/s │
│ Humidity        78% │  │ Direction       SW  │
│ Pressure    1012hPa │  │ Sunrise    05:43 AM │
│ Visibility   10.0km │  │ Sunset     08:52 PM │
╰─────────────────────╯  ╰─────────────────────╯
```

---

## 🛡️ Error Handling Framework

No developer logs or unexpected stack traces escape to the console. Every error scenario is mapped to explicit visual layouts:

| Error State | Raised Exception | Resolution Feedback Displayed |
| :--- | :--- | :--- |
| **Missing .env / Configuration** | `APIKeyMissingError` | System alerts that API key configuration is missing. |
| **Expired / Bad Keys** | `InvalidAPIKeyError` | Instructs user to verify their OpenWeatherMap API key validity. |
| **City Not Found** | `CityNotFoundError` | Explains the targeted city could not be resolved. |
| **Offline / Connection Drop** | `ConnectionError` | Alerts that communication with OpenWeatherMap failed. |
| **Timeout Reached** | `ConnectionError` | Notifies user that the server did not reply within the limit. |
| **Rate Limit Triggered** | `RateLimitError` | Informs user that they have sent too many requests. |
| **Data Parsing Error** | `ParsingError` | Indicates API sent bad or incomplete JSON payload. |

---

## 🧪 Testing & Validation Suite

The system comes with **149 fully functional unit and integration test cases** running against offline mock systems.

### Launch Test Runner
```bash
pytest tests/ -v
```

### Run with Coverage Verification
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Coverage Breakdowns
* **[test_validation.py](tests/test_validation.py)**: Validates input sanitization rules.
* **[test_parser.py](tests/test_parser.py)**: Ensures date math, compass directions, and icons map correctly under all conditions.
* **[test_api.py](tests/test_api.py)**: Evaluates response handling (including offline, timeout, 404, 401, and 500 statuses).
* **[test_display.py](tests/test_display.py)**: Captures console output to ensure terminal elements render properly.

---

## 🔐 Security & Logging Standards

* **Credential Protection**: The application loads the API key from environment variables. Keys are never written to disk or captured in log files.
* **Secure Logs**: Logs are kept locally in rotating files inside the `logs/` folder. They contain warnings, errors, and system activity records with time stamps, without violating user privacy.

---

## 🔮 Future Roadmap

* [ ] Add dynamic 5-Day forecast display utilizing visual progression timelines.
* [ ] Integrate Air Quality Index (AQI) values using the OpenWeather pollution API.
* [ ] Support standard SQL storage to preserve local search history logs.
* [ ] Offer option to export weather reports to `.csv` or `.json` formats.
* [ ] Build interactive auto-completions using fuzzy typing logic.
* [ ] Support standard imperial system units via dynamic program arguments.

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 👤 Author

**Kinza Kareem**

- GitHub: https://github.com/codewithkinza88
- LinkedIn: https://linkedin.com/in/kinza-kareem

---

<div align="center">

If this project helped you, please give it a star! ⭐

Made with ❤️ and ☕ using Python & Rich

*Made with dedication and precision*

</div>
