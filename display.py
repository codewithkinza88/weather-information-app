"""
display.py
----------
Rich-powered terminal UI for the Weather Information App.

This module is the *only* place that produces visible terminal output for
normal application flow.  All rendering is done with the ``rich`` library:
panels, tables, rules, and styled text are used consistently to produce a
premium CLI experience.

Functions are intentionally kept free of network or file I/O so that the
display logic can be exercised in unit tests by capturing ``Console`` output.
"""

from __future__ import annotations

from typing import Any

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

import config
from logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared console — a single instance is used throughout the app so that
# the Rich live-display context is consistent.
# ---------------------------------------------------------------------------
console = Console()

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

COLOUR_PRIMARY = "bold cyan"
COLOUR_SECONDARY = "bold yellow"
COLOUR_ACCENT = "bold magenta"
COLOUR_SUCCESS = "bold green"
COLOUR_ERROR = "bold red"
COLOUR_MUTED = "dim white"
COLOUR_HEADER = "bold white on dark_blue"
COLOUR_VALUE = "bright_white"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fmt_temp(value: Any) -> str:
    """Format a temperature value with the configured unit suffix."""
    if value == "N/A":
        return "N/A"
    return f"{float(value):.1f} {config.TEMP_UNIT}"


def _fmt_speed(value: Any) -> str:
    """Format a wind speed value with the configured unit suffix."""
    if value == "N/A":
        return "N/A"
    return f"{float(value):.1f} {config.SPEED_UNIT}"


def _fmt_pressure(value: Any) -> str:
    """Format a pressure value in hectopascals."""
    if value == "N/A":
        return "N/A"
    return f"{int(value)} hPa"


def _fmt_humidity(value: Any) -> str:
    """Format a relative humidity percentage."""
    if value == "N/A":
        return "N/A"
    return f"{int(value)} %"


def _fmt_visibility(value: Any) -> str:
    """Format a visibility distance in kilometres."""
    if value == "N/A":
        return "N/A"
    return f"{float(value):.1f} km"


# ---------------------------------------------------------------------------
# Public display functions
# ---------------------------------------------------------------------------


def display_welcome_banner() -> None:
    """
    Render the application welcome banner to the terminal.

    The banner includes the application name, version, and a decorative
    rule.  It is displayed once at application startup.
    """
    console.print()
    banner_text = Text(justify="center")
    banner_text.append("  🌤  ", style="bold yellow")
    banner_text.append(config.APP_NAME, style="bold cyan")
    banner_text.append("  🌤  ", style="bold yellow")

    version_text = Text(
        f"v{config.APP_VERSION}  •  Real-time weather powered by OpenWeatherMap",
        justify="center",
        style="dim cyan",
    )

    panel = Panel(
        Align.center(
            Text.assemble(
                banner_text,
                "\n",
                version_text,
            )
        ),
        border_style="bold cyan",
        padding=(1, 4),
        expand=True,
    )
    console.print(panel)
    console.print()


def display_weather(data: dict[str, Any]) -> None:
    """
    Render a full weather dashboard for the parsed weather *data*.

    The dashboard is composed of:

    * A location header panel showing city, country, coordinates, and
      the last-updated timestamp.
    * A condition strip showing the weather icon, description, and
      temperature summary.
    * A two-column metrics table covering atmosphere, wind, and
      astronomical data.

    Parameters
    ----------
    data:
        A parsed weather dictionary as produced by ``parser.parse_weather()``.
    """
    city: str = data.get("city", "Unknown")
    country: str = data.get("country", "??")
    lat: Any = data.get("latitude", "N/A")
    lon: Any = data.get("longitude", "N/A")
    icon: str = data.get("icon", "🌤️")
    description: str = data.get("description", "N/A")
    last_updated: str = data.get("last_updated", "N/A")

    # -----------------------------------------------------------------------
    # 1. Location header
    # -----------------------------------------------------------------------
    location_text = Text(justify="center")
    location_text.append(f"📍 {city}, {country}\n", style="bold white")

    try:
        lat_val = float(lat)
        lon_val = float(lon)
        lat_str = f"{abs(lat_val):.4f}°{'N' if lat_val >= 0 else 'S'}"
        lon_str = f"{abs(lon_val):.4f}°{'E' if lon_val >= 0 else 'W'}"
    except (TypeError, ValueError):
        lat_str = "N/A"
        lon_str = "N/A"
    coord_str = f"🛰  {lat_str}  {lon_str}   •   🕐 Updated: {last_updated}"
    location_text.append(coord_str, style="dim white")

    console.print(
        Panel(
            Align.center(location_text),
            border_style="cyan",
            padding=(0, 2),
        )
    )

    # -----------------------------------------------------------------------
    # 2. Condition strip
    # -----------------------------------------------------------------------
    temp = data.get("temperature", "N/A")
    feels = data.get("feels_like", "N/A")
    t_min = data.get("temp_min", "N/A")
    t_max = data.get("temp_max", "N/A")

    condition_text = Text(justify="center")
    condition_text.append(f"{icon}  ", style="bold yellow")
    condition_text.append(description, style="bold white")
    condition_text.append("\n")
    condition_text.append(_fmt_temp(temp), style="bold cyan")
    condition_text.append("  Feels like ", style="dim white")
    condition_text.append(_fmt_temp(feels), style="bold yellow")
    condition_text.append("\n")
    condition_text.append(f"Low  {_fmt_temp(t_min)}", style="bold blue")
    condition_text.append("   •   ", style="dim white")
    condition_text.append(f"High  {_fmt_temp(t_max)}", style="bold red")

    console.print(
        Panel(
            Align.center(condition_text),
            title=f"[bold yellow]☁  {data.get('condition', 'N/A')}[/bold yellow]",
            border_style="yellow",
            padding=(1, 4),
        )
    )

    # -----------------------------------------------------------------------
    # 3. Metrics tables — two side-by-side panels
    # -----------------------------------------------------------------------

    # --- Atmosphere & Humidity ---
    atm_table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        expand=True,
    )
    atm_table.add_column("Label", style="dim white", no_wrap=True)
    atm_table.add_column("Value", style="bold bright_white", justify="right")

    atm_table.add_row("🌡  Temperature", _fmt_temp(temp))
    atm_table.add_row("🌡  Feels Like", _fmt_temp(feels))
    atm_table.add_row("🌡  Min Temp", _fmt_temp(t_min))
    atm_table.add_row("🌡  Max Temp", _fmt_temp(t_max))
    atm_table.add_row("💧  Humidity", _fmt_humidity(data.get("humidity")))
    atm_table.add_row("🌐  Pressure", _fmt_pressure(data.get("pressure")))
    atm_table.add_row("👁  Visibility", _fmt_visibility(data.get("visibility_km")))

    atm_panel = Panel(
        atm_table,
        title="[bold cyan]🌡  Atmosphere[/bold cyan]",
        border_style="cyan",
        padding=(0, 1),
    )

    # --- Wind & Sun ---
    wind_table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        expand=True,
    )
    wind_table.add_column("Label", style="dim white", no_wrap=True)
    wind_table.add_column("Value", style="bold bright_white", justify="right")

    wind_table.add_row("🌬  Wind Speed", _fmt_speed(data.get("wind_speed")))
    wind_table.add_row("🧭  Wind Direction", data.get("wind_direction", "N/A"))
    wind_table.add_row("🌅  Sunrise", data.get("sunrise", "N/A"))
    wind_table.add_row("🌇  Sunset", data.get("sunset", "N/A"))
    wind_table.add_row("🕐  Timezone", _format_timezone(data.get("timezone_offset", 0)))
    wind_table.add_row("🗺  Latitude", lat_str)
    wind_table.add_row("🗺  Longitude", lon_str)

    wind_panel = Panel(
        wind_table,
        title="[bold magenta]🌬  Wind & Sun[/bold magenta]",
        border_style="magenta",
        padding=(0, 1),
    )

    console.print(Columns([atm_panel, wind_panel], equal=True))
    console.print()


def _format_timezone(offset_seconds: int) -> str:
    """
    Convert a UTC offset in seconds to a human-readable string.

    Parameters
    ----------
    offset_seconds:
        UTC offset in seconds (may be negative).

    Returns
    -------
    str
        Formatted as ``"UTC+5:30"`` or ``"UTC-3:00"``.
    """
    sign = "+" if offset_seconds >= 0 else "-"
    total_minutes = abs(offset_seconds) // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"UTC{sign}{hours}:{minutes:02d}"


def display_error(title: str, message: str, details: str = "") -> None:
    """
    Render a styled error panel to the terminal.

    Parameters
    ----------
    title:
        Short error category, e.g. ``"City Not Found"``.
    message:
        User-facing explanation of the error.
    details:
        Optional technical detail shown below the main message.
    """
    error_text = Text()
    error_text.append(f"  ✖  {message}", style="bold red")
    if details:
        error_text.append(f"\n\n  {details}", style="dim white")

    console.print(
        Panel(
            error_text,
            title=f"[bold red]⚠  {title}[/bold red]",
            border_style="red",
            padding=(0, 2),
        )
    )
    console.print()
    log.debug("Displayed error — title='%s', message='%s'", title, message)


def display_info(message: str) -> None:
    """Render a single styled informational line."""
    console.print(f"  [dim cyan]ℹ  {message}[/dim cyan]")


def display_success(message: str) -> None:
    """Render a single styled success line."""
    console.print(f"  [bold green]✔  {message}[/bold green]")


def display_rule(title: str = "") -> None:
    """Render a horizontal rule, optionally with a centred title."""
    console.print(Rule(title=title, style="dim cyan"))


def prompt_city() -> str:
    """
    Prompt the user to enter a city name and return the raw input.

    Returns
    -------
    str
        The raw (un-stripped, un-validated) string entered by the user.
    """
    console.print()
    console.print("  [bold cyan]🔍  Enter a city name:[/bold cyan] ", end="")
    return input()


def prompt_continue() -> bool:
    """
    Ask whether the user wants to search for another city.

    Returns
    -------
    bool
        ``True`` if the user enters ``y`` or ``yes``; ``False`` otherwise.
    """
    console.print()
    console.print(
        "  [bold cyan]🔄  Search another city?[/bold cyan] "
        "[dim white](y/n):[/dim white] ",
        end="",
    )
    answer = input().strip().lower()
    return answer in {"y", "yes"}


def display_goodbye() -> None:
    """Render a friendly farewell message before the application exits."""
    console.print()
    console.print(
        Panel(
            Align.center(
                Text.assemble(
                    ("  Thank you for using  ", "dim white"),
                    (config.APP_NAME, "bold cyan"),
                    ("  🌤  \n", "bold yellow"),
                    ("Stay safe and enjoy your day! ☀️", "dim white"),
                )
            ),
            border_style="cyan",
            padding=(1, 4),
        )
    )
    console.print()
