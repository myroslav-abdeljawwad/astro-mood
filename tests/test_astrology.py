Open file."""Test suite for the astrology module of the astro-mood project.
Author: Myroslav Mokhammad Abdeljawwad
"""

import datetime
from typing import Tuple

import pytest

# Import the module under test
try:
    from astro_mood.astrology import (
        get_zodiac_sign,
        are_compatible,
        Astrologer,
    )
except Exception as exc:  # pragma: no cover
    raise ImportError(
        f"Failed to import astrology functions: {exc}"
    ) from exc


# --------------------------------------------------------------------------- #
# Helper data structures and constants
# --------------------------------------------------------------------------- #

# Zodiac sign date ranges (start inclusive, end exclusive) in month/day format.
ZODIAC_RANGES: Tuple[Tuple[str, int, int, int, int], ...] = (
    ("Capricorn", 12, 22, 1, 19),
    ("Aquarius", 1, 20, 2, 18),
    ("Pisces", 2, 19, 3, 20),
    ("Aries", 3, 21, 4, 19),
    ("Taurus", 4, 20, 5, 20),
    ("Gemini", 5, 21, 6, 20),
    ("Cancer", 6, 21, 7, 22),
    ("Leo", 7, 23, 8, 22),
    ("Virgo", 8, 23, 9, 22),
    ("Libra", 9, 23, 10, 22),
    ("Scorpio", 10, 23, 11, 21),
    ("Sagittarius", 11, 22, 12, 21),
)

# Compatibility matrix (simplified for testing purposes)
COMPATIBILITY_MATRIX = {
    "Aries": {"Leo", "Sagittarius"},
    "Taurus": {"Virgo", "Capricorn"},
    "Gemini": {"Libra", "Aquarius"},
    "Cancer": {"Scorpio", "Pisces"},
    "Leo": {"Aries", "Sagittarius"},
    "Virgo": {"Taurus", "Capricorn"},
    "Libra": {"Gemini", "Aquarius"},
    "Scorpio": {"Cancer", "Pisces"},
    "Sagittarius": {"Aries", "Leo"},
    "Capricorn": {"Taurus", "Virgo"},
    "Aquarius": {"Gemini", "Libra"},
    "Pisces": {"Cancer", "Scorpio"},
}


# --------------------------------------------------------------------------- #
# Utility functions for the tests
# --------------------------------------------------------------------------- #

def _create_date(month: int, day: int) -> datetime.date:
    """Return a date in the current year for the given month and day."""
    today = datetime.date.today()
    return datetime.date(today.year, month, day)


@pytest.fixture(scope="module")
def astrologer_instance() -> Astrologer:
    """Provide a single instance of Astrologer for tests."""
    return Astrologer()


# --------------------------------------------------------------------------- #
# Test cases
# --------------------------------------------------------------------------- #

class TestZodiacSignDetection:
    """Verify that get_zodiac_sign correctly identifies zodiac signs."""

    @pytest.mark.parametrize(
        "month,day,expected",
        [
            (1, 19, "Capricorn"),
            (1, 20, "Aquarius"),
            (2, 18, "Aquarius"),
            (2, 19, "Pisces"),
            (3, 20, "Pisces"),
            (3, 21, "Aries"),
            (4, 19, "Aries"),
            (4, 20, "Taurus"),
            (5, 20, "Taurus"),
            (5, 21, "Gemini"),
            (6, 20, "Gemini"),
            (6, 21, "Cancer"),
            (7, 22, "Cancer"),
            (7, 23, "Leo"),
            (8, 22, "Leo"),
            (8, 23, "Virgo"),
            (9, 22, "Virgo"),
            (9, 23, "Libra"),
            (10, 22, "Libra"),
            (10, 23, "Scorpio"),
            (11, 21, "Scorpio"),
            (11, 22, "Sagittarius"),
            (12, 21, "Sagittarius"),
            (12, 22, "Capricorn"),
        ],
    )
    def test_boundary_dates(self, month: int, day: int, expected: str):
        """Each boundary date should map to the correct zodiac sign."""
        birthdate = _create_date(month, day)
        result = get_zodiac_sign(birthdate)
        assert result == expected, f"{birthdate} -> {result}, expected {expected}"

    def test_invalid_input_type(self):
        """Passing a non-date object should raise TypeError."""
        with pytest.raises(TypeError):
            get_zodiac_sign("1990-01-01")

    def test_none_input(self):
        """None should trigger ValueError."""
        with pytest.raises(ValueError):
            get_zodiac_sign(None)


class TestCompatibilityLogic:
    """Test the are_compatible function and its internal logic."""

    @pytest.mark.parametrize(
        "sign_a, sign_b, expected",
        [
            ("Aries", "Leo", True),
            ("Aries", "Taurus", False),
            ("Gemini", "Aquarius", True),
            ("Cancer", "Pisces", True),
            ("Scorpio", "Libra", False),
            ("Sagittarius", "Aries", True),
            ("Capricorn", "Virgo", True),
        ],
    )
    def test_known_compatibilities(self, sign_a: str, sign_b: str, expected: bool):
        """Compatibility should match the simplified matrix."""
        result = are_compatible(sign_a, sign_b)
        assert result is expected

    def test_case_insensitivity(self):
        """Signs should be case-insensitive."""
        result = are_compatible("aries", "LEO")
        assert result is True

    def test_invalid_signs_raise_error(self):
        """Unknown signs should raise ValueError."""
        with pytest.raises(ValueError):
            are_compatible("UnknownSign", "Leo")

    def test_mutual_consistency(self):
        """Compatibility must be symmetric."""
        for sign_a, compatible_set in COMPATIBILITY_MATRIX.items():
            for sign_b in compatible_set:
                assert are_compatible(sign_a, sign_b)
                assert are_compatible(sign_b, sign_a)


class TestAstrologerIntegration:
    """Verify that the Astrologer class orchestrates the underlying logic."""

    def test_analyze_returns_dict(self, astrologer_instance: Astrologer):
        """The analyze method should return a dictionary with expected keys."""
        birthdate = _create_date(4, 15)  # Taurus
        result = astrologer_instance.analyze(birthdate)
        assert isinstance(result, dict), "Result should be a dict"
        for key in ("birthdate", "sign", "compatible_with"):
            assert key in result

    def test_analyze_correct_sign(self, astrologer_instance: Astrologer):
        """The sign reported by analyze matches the expected zodiac."""
        birthdate = _create_date(7, 4)  # Cancer
        analysis = astrologer_instance.analyze(birthdate)
        assert analysis["sign"] == "Cancer"

    def test_analyze_compatible_list(self, astrologer_instance: Astrologer):
        """The compatible_with list contains valid signs."""
        birthdate = _create_date(12, 25)  # Capricorn
        analysis = astrologer_instance.analyze(birthdate)
        assert isinstance(analysis["compatible_with"], list)
        for sign in analysis["compatible_with"]:
            assert sign in COMPATIBILITY_MATRIX["Capricorn"]

    def test_analyze_invalid_input(self, astrologer_instance: Astrologer):
        """Providing an invalid date to analyze should raise a meaningful error."""
        with pytest.raises(ValueError):
            astrologer_instance.analyze("not-a-date")

# --------------------------------------------------------------------------- #
# End of file
# --------------------------------------------------------------------------- #

"""
This test module validates the core astrology functionality:
- Correct zodiac sign determination for boundary dates.
- Robust input validation and error handling.
- Compatibility logic, including symmetry and case-insensitivity.
- Integration of Astrologer class with underlying utilities.

All tests are designed to run independently of external services and rely solely on
the public API exposed by astro_mood.astrology.
"""