"""
astro-mood main entry point
Author: Myroslav Mokhammad Abdeljawwad

This module orchestrates the core functionality of the astro‑mood package:
* Loads configuration from a YAML file.
* Retrieves the current lunar phase via :mod:`astro_mood.moon`.
* Determines the zodiac sign for today via :mod:`astro_mood.astrology`.
* Prints a concise, human‑readable report.

The command line interface defined in :mod:`astro_mood.cli` delegates to this
module through the ``main`` function, which is also exposed as the console
script entry point.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

# Local imports – these modules expose well‑defined public APIs
try:
    from .settings import load_config  # type: ignore[attr-defined]
except Exception as exc:  # pragma: no cover - defensive
    raise RuntimeError("Failed to import settings module") from exc

try:
    from .moon import get_lunar_phase, LunarPhase  # type: ignore[attr-defined]
except Exception as exc:  # pragma: no cover - defensive
    raise RuntimeError("Failed to import moon module") from exc

try:
    from .astrology import get_zodiac_sign  # type: ignore[attr-defined]
except Exception as exc:  # pragma: no cover - defensive
    raise RuntimeError("Failed to import astrology module") from exc


__all__ = ["main", "report"]


def _today() -> _dt.date:
    """Return today's date in UTC."""
    return _dt.datetime.utcnow().date()


def report(config_path: Path | None = None) -> str:
    """
    Generate a textual report of the current lunar phase and zodiac sign.

    Parameters
    ----------
    config_path : pathlib.Path, optional
        Path to a YAML configuration file. If omitted, defaults to
        ``~/.config/astro_mood/config.yaml``. The configuration may contain user
        preferences such as language or output format, but for this simplified
        implementation we only validate its existence.

    Returns
    -------
    str
        A formatted string ready for printing.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    """
    if config_path is None:
        home = Path.home()
        config_path = home / ".config" / "astro_mood" / "config.yaml"

    # Validate configuration file presence
    if not config_path.is_file():
        raise FileNotFoundError(f"No configuration found at {config_path}")

    # Load (and ignore) the actual settings – the load_config function will
    # perform any necessary validation and return a dictionary.
    try:
        _ = load_config(config_path)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Configuration error: {exc}") from exc

    today = _today()
    phase = get_lunar_phase(today)  # type: ignore[call-arg]
    zodiac = get_zodiac_sign(today)

    return (
        f"Today is {today.isoformat()}.\n"
        f"Lunar Phase: {phase.value}\n"
        f"Zodiac Sign: {zodiac}"
    )


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the console script.

    Parameters
    ----------
    argv : list of str, optional
        Command line arguments excluding the program name. If ``None``,
        ``sys.argv[1:]`` is used.

    Returns
    -------
    int
        Exit code (0 on success, non‑zero on failure).
    """
    if argv is None:
        argv = sys.argv[1:]

    # Simple argument parsing: support --config PATH and --help
    config_path = None
    show_help = False

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            show_help = True
            break
        elif arg in ("--config", "-c") and i + 1 < len(argv):
            config_path = Path(argv[i + 1]).expanduser()
            i += 1
        else:
            print(f"Unknown argument: {arg}", file=sys.stderr)
            return 2
        i += 1

    if show_help:
        help_text = """
astro-mood - Sync your creativity with the cosmos

Usage:
  astro_mood [--config PATH]

Options:
  -h, --help          Show this message and exit.
  -c, --config PATH   Path to configuration file (default: ~/.config/astro_mood/config.yaml)
"""
        print(help_text.strip())
        return 0

    try:
        out = report(Path(config_path) if config_path else None)
        print(out)
        return 0
    except FileNotFoundError as fnf_err:
        print(f"Configuration error: {fnf_err}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 3

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())