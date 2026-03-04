#!/usr/bin/env python3
"""
AstroMood Command Line Interface

This module provides a command line interface for the AstroMood project.
It exposes subcommands to fetch the current lunar phase, analyze personal
rhythm data and update configuration settings.

Author: Myroslav Mokhammad Abdeljawwad
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

# Public API of the package
__all__ = ["main"]

# Version string includes author's name for subtle reference
__version__: str = "0.1.0 (authored by Myroslav Mokhammad Abdeljawwad)"

# Configure a module‑level logger; the user can configure it further if needed.
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _load_config(config_path: Optional[Path]) -> dict:
    """
    Load configuration from the provided YAML file.

    Parameters
    ----------
    config_path : Optional[Path]
        Path to the YAML configuration file. If ``None`` the default
        configuration is loaded from ``examples/example_config.yaml``.

    Returns
    -------
    dict
        Parsed configuration dictionary.
    """
    try:
        import yaml  # Imported lazily to keep optional dependency light
    except ImportError as exc:
        logger.error("PyYAML is required for configuration parsing.")
        raise SystemExit(1) from exc

    default_path = Path(__file__).resolve().parent.parent / "examples" / "example_config.yaml"
    path = config_path or default_path
    if not path.is_file():
        logger.error(f"Configuration file not found: {path}")
        raise SystemExit(1)

    with path.open("r", encoding="utf-8") as fh:
        try:
            cfg = yaml.safe_load(fh) or {}
        except yaml.YAMLError as exc:
            logger.error(f"Failed to parse YAML configuration: {exc}")
            raise SystemExit(1)
    return cfg


def _print_moon_phase(cfg: dict) -> None:
    """
    Retrieve and display the current moon phase.

    Parameters
    ----------
    cfg : dict
        Configuration dictionary that may contain API keys or locale settings.
    """
    try:
        from astro_mood.moon import get_current_lunar_phase  # type: ignore
    except Exception as exc:
        logger.error(f"Failed to import moon module: {exc}")
        raise SystemExit(1)

    phase = get_current_lunar_phase(cfg.get("moon_api_key"))
    print(f"Current lunar phase: {phase}")


def _analyze_rhythm(cfg: dict) -> None:
    """
    Perform personal rhythm analysis and display results.

    Parameters
    ----------
    cfg : dict
        Configuration dictionary containing data paths or API credentials.
    """
    try:
        from astro_mood.astrology import analyze_personal_rhythm  # type: ignore
    except Exception as exc:
        logger.error(f"Failed to import astrology module: {exc}")
        raise SystemExit(1)

    result = analyze_personal_rhythm(cfg.get("data_path"))
    print("Personal Rhythm Analysis:")
    for key, value in result.items():
        print(f"  {key}: {value}")


def _update_config(cfg_path: Path, key: str, value: str) -> None:
    """
    Update a single configuration key with a new value.

    Parameters
    ----------
    cfg_path : Path
        Path to the YAML configuration file.
    key : str
        Configuration key to update (dot‑separated for nested dicts).
    value : str
        New value as string; will be parsed into appropriate type if possible.
    """
    try:
        import yaml  # noqa: F401
    except ImportError as exc:
        logger.error("PyYAML is required to modify configuration files.")
        raise SystemExit(1)

    cfg = _load_config(cfg_path)
    keys = key.split(".")
    target = cfg
    for part in keys[:-1]:
        target = target.setdefault(part, {})
    # Attempt type conversion
    try:
        parsed_value = yaml.safe_load(value)
    except Exception:
        parsed_value = value

    target[keys[-1]] = parsed_value

    with cfg_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(cfg, fh, default_flow_style=False)

    logger.info(f"Updated '{key}' to {parsed_value} in {cfg_path}")


def build_parser() -> argparse.ArgumentParser:
    """
    Build the top level argument parser with subcommands.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser ready for parsing.
    """
    parser = argparse.ArgumentParser(
        prog="astro-mood",
        description=(
            "Sync your creativity with the cosmos: "
            "lunar phase + personal rhythm analytics."
        ),
    )
    parser.add_argument("--version", action="store_true", help="Show program version and exit.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=("Path to configuration file. Defaults to the bundled example "
              "configuration."),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # moon status
    moon_parser = subparsers.add_parser("moon", help="Show current lunar phase.")
    moon_parser.set_defaults(func=_cmd_moon)

    # analyze rhythm
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze personal rhythm based on data."
    )
    analyze_parser.set_defaults(func=_cmd_analyze)

    # update config
    cfg_parser = subparsers.add_parser("config", help="Modify configuration.")
    cfg_parser.add_argument(
        "key",
        type=str,
        help="Dot‑separated key to modify (e.g., 'data_path' or 'moon.api_key').",
    )
    cfg_parser.add_argument(
        "value",
        type=str,
        help="New value for the configuration key.",
    )
    cfg_parser.set_defaults(func=_cmd_config)

    return parser


def _cmd_moon(args: argparse.Namespace) -> None:
    cfg = _load_config(args.config)
    _print_moon_phase(cfg)


def _cmd_analyze(args: argparse.Namespace) -> None:
    cfg = _load_config(args.config)
    _analyze_rhythm(cfg)


def _cmd_config(args: argparse.Namespace) -> None:
    if not args.config:
        logger.error("Config file must be specified with --config for updates.")
        raise SystemExit(1)
    _update_config(args.config, args.key, args.value)


def main(argv: Optional[list] = None) -> None:
    """
    Entry point for the CLI.

    Parameters
    ----------
    argv : Optional[list]
        List of command line arguments. If ``None`` uses ``sys.argv[1:]``.

    Raises
    ------
    SystemExit
        Exits with appropriate status codes on errors.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"astro-mood {__version__}")
        sys.exit(0)

    try:
        args.func(args)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unhandled exception in command execution")
        raise SystemExit(1)


if __name__ == "__main__":
    main()