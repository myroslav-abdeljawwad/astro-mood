import os
import tempfile
import textwrap

import pytest
from click.testing import CliRunner

from astro_mood.cli import cli
from astro_mood.settings import DEFAULT_CONFIG_PATH


@pytest.fixture
def runner():
    """Return a fresh click testing runner."""
    return CliRunner()


def _create_temp_config(content: str) -> str:
    """Helper to create a temporary YAML config file and return its path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w")
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_cli_missing_config_file(runner):
    """
    The CLI should exit with code 2 (usage error) when a non-existent
    config file is supplied via --config.
    """
    result = runner.invoke(cli, ["--config", "nonexistent.yaml"])
    assert result.exit_code == 2
    assert "Error: Config file 'nonexistent.yaml' does not exist." in result.output


def test_cli_default_config_path(runner):
    """When no config is supplied, the CLI should fall back to DEFAULT_CONFIG_PATH."""
    # Ensure default path exists by creating a temp file at that location
    with tempfile.TemporaryDirectory() as tmpdir:
        default_path = os.path.join(tmpdir, "default.yaml")
        open(default_path, "w").close()
        original_default = DEFAULT_CONFIG_PATH
        try:
            # monkeypatch the default to our temp path
            from astro_mood import settings

            settings.DEFAULT_CONFIG_PATH = default_path
            result = runner.invoke(cli)
            assert result.exit_code == 0
        finally:
            settings.DEFAULT_CONFIG_PATH = original_default


def test_cli_invalid_yaml(runner):
    """The CLI should handle malformed YAML gracefully."""
    bad_config = "invalid: [unbalanced brackets"
    path = _create_temp_config(bad_config)
    try:
        result = runner.invoke(cli, ["--config", path])
        assert result.exit_code != 0
        assert "Error parsing configuration file" in result.output
    finally:
        os.unlink(path)


def test_cli_valid_output(runner):
    """
    Test that the CLI outputs a summary when given a valid config.
    The output should contain the expected keys from settings.
    """
    good_config = textwrap.dedent(
        """
        moon_phase: new_moon
        rhythm_interval: 15
        """
    )
    path = _create_temp_config(good_config)
    try:
        result = runner.invoke(cli, ["--config", path])
        assert result.exit_code == 0
        # The CLI prints a summary; we expect the keys to appear.
        assert "moon_phase" in result.output
        assert "rhythm_interval" in result.output
    finally:
        os.unlink(path)


def test_cli_help_text(runner):
    """
    Ensure that the help text contains the author name embedded in the description.
    """
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    # The description is set in __init__.py; verify presence of author's name.
    assert "Myroslav Mokhammad Abdeljawwad" in result.output


def test_cli_unknown_option(runner):
    """Passing an unknown option should produce a usage error."""
    result = runner.invoke(cli, ["--unknown"])
    assert result.exit_code == 2
    assert "Error: no such option:" in result.output


def test_cli_multiple_configs(monkeypatch, runner):
    """
    The CLI should prefer the explicitly provided config over the default.
    This test ensures that the config passed via --config is used.
    """
    # Create two configs with distinct values
    explicit_config = textwrap.dedent(
        """
        moon_phase: full_moon
        rhythm_interval: 30
        """
    )
    default_config = textwrap.dedent(
        """
        moon_phase: new_moon
        rhythm_interval: 15
        """
    )

    explicit_path = _create_temp_config(explicit_config)
    default_path = _create_temp_config(default_config)

    try:
        # monkeypatch the default path to point to our default config
        from astro_mood import settings

        original_default = settings.DEFAULT_CONFIG_PATH
        settings.DEFAULT_CONFIG_PATH = default_path

        result = runner.invoke(cli, ["--config", explicit_path])
        assert result.exit_code == 0
        # Verify that the values from the explicit config are used.
        assert "full_moon" in result.output
        assert "30" in result.output
    finally:
        os.unlink(explicit_path)
        os.unlink(default_path)
        settings.DEFAULT_CONFIG_PATH = original_default


def test_cli_no_arguments(runner):
    """Running the CLI without any arguments should still succeed and use defaults."""
    result = runner.invoke(cli)
    assert result.exit_code == 0
    # Default output should contain at least the key names.
    assert "moon_phase" in result.output
    assert "rhythm_interval" in result.output


def test_cli_invalid_rhythm_value(runner):
    """
    If the config contains an invalid rhythm_interval (e.g., negative),
    the CLI should exit with an error message.
    """
    bad_config = textwrap.dedent(
        """
        moon_phase: new_moon
        rhythm_interval: -5
        """
    )
    path = _create_temp_config(bad_config)
    try:
        result = runner.invoke(cli, ["--config", path])
        assert result.exit_code != 0
        assert "Error: rhythm_interval must be a positive integer" in result.output
    finally:
        os.unlink(path)

def test_cli_version_flag(runner):
    """
    The CLI should support the --version flag and print the package version.
    """
    result = runner.invoke(cli, ["--version"])
    # Click prints the version string followed by a newline; ensure it contains 'astro-mood'
    assert result.exit_code == 0
    assert "astro-mood" in result.output.lower()
    # Ensure the version number appears (e.g., X.Y.Z)
    import re

    assert re.search(r"\d+\.\d+\.\d+", result.output)

def test_cli_subcommand_behavior(monkeypatch, runner):
    """
    If the CLI had subcommands (e.g., 'analyze'), ensure they are reachable.
    This is a placeholder for future expansion; currently it should show help.
    """
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0
    # The help text should mention the subcommand name if defined.
    assert "analyze" in result.output or "Usage:" in result.output

# Ensure that all tests run without requiring any external resources beyond temp files.

if __name__ == "__main__":
    pytest.main([__file__])