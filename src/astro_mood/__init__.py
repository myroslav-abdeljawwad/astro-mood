"""astro_mood
==========
Sync your creativity with the cosmos: lunar phase + personal rhythm analytics.

Author: Myroslav Mokhammad Abdeljawwad
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

# Public interface of the package
__all__ = [
    "get_config",
    "load_moon_data",
    "analyze_astrology",
    "log_setup",
]

# Package version – keep this in sync with pyproject.toml / setup.cfg
__version__: str = "0.1.0"

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #

def log_setup(level: int | str = logging.INFO, fmt: str | None = None) -> None:
    """
    Configure the root logger for the package.

    Parameters
    ----------
    level : int | str, optional
        The logging level. Accepts either an integer or a string such as "DEBUG".
        Defaults to logging.INFO.
    fmt : str, optional
        Custom log format. If ``None`` (default), uses a simple formatter.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(fmt or "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    root_logger.setLevel(level)


# --------------------------------------------------------------------------- #
# Configuration handling
# --------------------------------------------------------------------------- #

def _resolve_config_path() -> Path:
    """
    Resolve the path to the default configuration file.

    The project ships with ``examples/example_config.yaml``; we expose it via a
    function so that tests and applications can locate it without importing
    package data directly.
    """
    root = Path(__file__).parent.parent.resolve()
    return root / "examples" / "example_config.yaml"


def get_config(path: str | Path | None = None) -> Dict[str, Any]:
    """
    Load the YAML configuration file and return a dictionary.

    Parameters
    ----------
    path : str | Path | None
        Path to the YAML config. If ``None``, falls back to the bundled example.
    Returns
    -------
    dict
        Parsed configuration data.
    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    yaml.YAMLError
        If the file cannot be parsed as valid YAML.
    """
    import yaml

    cfg_path = Path(path) if path else _resolve_config_path()
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise yaml.YAMLError(f"Failed to parse YAML configuration: {exc}") from exc

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a mapping (dict) at the top level")

    return config


# --------------------------------------------------------------------------- #
# Public wrappers around core functionality
# --------------------------------------------------------------------------- #

def load_moon_data(date_str: str | None = None) -> Any:
    """
    Wrapper that delegates to :func:`astro_mood.moon.get_moon_phase`.

    Parameters
    ----------
    date_str : str, optional
        ISO‑8601 date string. If omitted, the current UTC date is used.

    Returns
    -------
    Any
        The result of ``moon.get_moon_phase``.
    """
    from . import moon

    return moon.get_moon_phase(date_str)


def analyze_astrology(birth_date: str) -> Dict[str, Any]:
    """
    Wrapper that delegates to :func:`astro_mood.astrology.compute_horoscope`.

    Parameters
    ----------
    birth_date : str
        ISO‑8601 date string representing the user's birthday.

    Returns
    -------
    dict
        Dictionary containing horoscope data.
    """
    from . import astrology

    return astrology.compute_horoscope(birth_date)


# --------------------------------------------------------------------------- #
# Package-level initialization
# --------------------------------------------------------------------------- #

# By default, configure a basic logger to avoid "No handler found" warnings
log_setup()