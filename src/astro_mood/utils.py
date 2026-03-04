"""Utility helpers for the astro-mood project.
Author: Myroslav Mokhammad Abdeljawwad
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import sys
import time
from datetime import datetime, date, timedelta
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

# --------------------------------------------------------------------------- #
# Logging configuration – useful for debugging without polluting stdout
# --------------------------------------------------------------------------- #

_logger = logging.getLogger(__name__)
if not _logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s"
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


# --------------------------------------------------------------------------- #
# Configuration helpers
# --------------------------------------------------------------------------- #

def load_json_config(file_path: Union[str, pathlib.Path]) -> Dict[str, Any]:
    """
    Load a JSON configuration file and return its contents as a dictionary.
    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path = pathlib.Path(file_path).expanduser().resolve()
    _logger.debug("Loading config from %s", path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file {path} does not exist.")
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    _logger.debug("Config loaded: %s keys", len(data))
    return data


def merge_configs(
    base: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Recursively merge two configuration dictionaries.
    Values in ``overrides`` take precedence over those in ``base``.
    """
    if overrides is None:
        return base.copy()

    result = base.copy()
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result


# --------------------------------------------------------------------------- #
# Date/Time helpers
# --------------------------------------------------------------------------- #

def parse_iso_date(date_str: str) -> date:
    """
    Parse an ISO‑8601 date string (YYYY-MM-DD) into a :class:`datetime.date`.
    Raises ValueError on failure.
    """
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
        _logger.debug("Parsed ISO date %s -> %s", date_str, parsed)
        return parsed
    except Exception as exc:
        raise ValueError(f"Invalid ISO date format: {date_str}") from exc


def parse_datetime(dt_str: str) -> datetime:
    """
    Parse a datetime string in RFC3339/ISO8601 with optional timezone.
    Falls back to naive datetime if no timezone is present.
    """
    try:
        # Python 3.11+ supports fromisoformat with timezone
        parsed = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        _logger.debug("Parsed datetime %s -> %s", dt_str, parsed)
        return parsed
    except Exception as exc:
        raise ValueError(f"Invalid datetime format: {dt_str}") from exc


def to_iso_date(d: date) -> str:
    """Return ISO string representation of a :class:`datetime.date`."""
    iso = d.isoformat()
    _logger.debug("Converted %s to ISO date string %s", d, iso)
    return iso


def to_rfc3339(dt: datetime) -> str:
    """Return RFC3339 string from a :class:`datetime.datetime`. """
    rfc = dt.astimezone().isoformat(timespec="seconds")
    _logger.debug("Converted %s to RFC3339 string %s", dt, rfc)
    return rfc


# --------------------------------------------------------------------------- #
# Moon phase calculation helpers
# --------------------------------------------------------------------------- #

@lru_cache(maxsize=256)
def _calculate_moon_age(d: date) -> float:
    """
    Return the moon age in days for a given calendar date.
    Algorithm based on Conway's algorithm – accurate to within 1‑2 days.
    """
    # Reference: https://www.voidware.com/moon_phase.htm
    y = d.year
    m = d.month
    if m < 3:
        y -= 1
        m += 12
    k = int(365.25 * (y + 4712))
    n = int(30.6 * (m + 1)) + d.day + k - 694039.09
    n = n / 29.5305882  # full lunar cycle
    age = n % 1
    days_into_cycle = round(age * 29.53, 3)
    _logger.debug("Calculated moon age for %s: %.3f days", d, days_into_cycle)
    return days_into_cycle


def get_moon_phase(d: Union[date, str]) -> Tuple[str, float]:
    """
    Return the current lunar phase name and its age in days.
    Accepts a :class:`datetime.date` or ISO date string.

    Returns:
        (phase_name, age_in_days)
    """
    if isinstance(d, str):
        d = parse_iso_date(d)

    age = _calculate_moon_age(d)
    # Determine phase based on age thresholds
    if age < 1.84566:
        phase = "New Moon"
    elif age < 5.53699:
        phase = "Waxing Crescent"
    elif age < 9.22831:
        phase = "First Quarter"
    elif age < 12.91963:
        phase = "Waxing Gibbous"
    elif age < 16.61096:
        phase = "Full Moon"
    elif age < 20.30228:
        phase = "Waning Gibbous"
    elif age < 23.99361:
        phase = "Last Quarter"
    else:
        phase = "Waning Crescent"

    _logger.debug("Moon phase for %s: %s (age %.3f days)", d, phase, age)
    return phase, round(age, 3)


# --------------------------------------------------------------------------- #
# File path utilities
# --------------------------------------------------------------------------- #

def get_user_config_path() -> pathlib.Path:
    """
    Return the default configuration file path in the user's home directory.
    """
    config_file = pathlib.Path.home() / ".config" / "astro-mood" / "config.json"
    _logger.debug("User config path: %s", config_file)
    return config_file


def ensure_directory_exists(path: Union[str, pathlib.Path]) -> None:
    """Create the directory for ``path`` if it does not exist."""
    dir_path = pathlib.Path(path).expanduser().resolve()
    if not dir_path.is_dir():
        _logger.debug("Creating missing directory %s", dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Simple caching decorator for arbitrary functions
# --------------------------------------------------------------------------- #

def memoize(seconds: int = 60):
    """
    Decorator that caches function results in memory for a given number of seconds.
    Useful for expensive computations or API calls.

    Example:
        @memoize(120)
        def heavy_calculation(x):
            ...
    """

    def decorator(func):
        cache: Dict[Tuple[Any, ...], Tuple[Any, float]] = {}

        def wrapper(*args, **kwargs):
            key = args + tuple(sorted(kwargs.items()))
            now = time.time()
            if key in cache:
                result, ts = cache[key]
                if now - ts < seconds:
                    _logger.debug("Cache hit for %s", func.__name__)
                    return result
            _logger.debug("Cache miss for %s; computing", func.__name__)
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper

    return decorator


# --------------------------------------------------------------------------- #
# Data normalization helpers
# --------------------------------------------------------------------------- #

def normalize_text(text: str) -> str:
    """
    Normalize a string to lowercase and strip surrounding whitespace.
    Useful for user input matching.
    """
    normalized = text.strip().lower()
    _logger.debug("Normalized '%s' -> '%s'", text, normalized)
    return normalized


def validate_email(email: str) -> bool:
    """Simple regex‑based email validation."""
    import re

    pattern = r"^[\w.+-]+@[\w.-]+\.\w+$"
    valid = re.match(pattern, email.strip()) is not None
    _logger.debug("Email %s validity: %s", email, valid)
    return valid


# --------------------------------------------------------------------------- #
# Version information
# --------------------------------------------------------------------------- #

__version__: str = "0.1.0"

if __name__ == "__main__":
    # Quick sanity checks when running this module directly
    logging.basicConfig(level=logging.DEBUG)
    sample_date = date.today()
    phase, age = get_moon_phase(sample_date)
    print(f"Today ({sample_date}) – {phase} (age {age:.2f} days)")
    cfg_path = get_user_config_path()
    print("User config path:", cfg_path)