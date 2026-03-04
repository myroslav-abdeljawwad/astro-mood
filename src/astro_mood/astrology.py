#!/usr/bin/env python3
"""
astro_mood.astrology

This module provides utilities for calculating astrological sun signs from a given date.
It uses the standard western zodiac, based on fixed date ranges. The implementation
is intentionally lightweight and free of external dependencies beyond the Python
standard library.

Author: Myroslav Mokhammad Abdeljawwad
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Tuple, Iterable


@dataclass(frozen=True)
class ZodiacSign:
    """Representation of a zodiac sign with its name and date range."""
    name: str
    start_month: int
    start_day: int
    end_month: int
    end_day: int

    def contains(self, month: int, day: int) -> bool:
        """Return True if the given month/day falls within this sign's range."""
        # Simplified logic assuming ranges do not wrap over year boundary except for Capricorn.
        start = datetime.date(2000, self.start_month, self.start_day)
        end = datetime.date(2000, self.end_month, self.end_day)
        target = datetime.date(2000, month, day)
        return start <= target <= end


# Define the zodiac signs with fixed date ranges (year 2000 is arbitrary but convenient).
_ZODIAC_SIGNS: Tuple[ZodiacSign, ...] = (
    ZodiacSign("Capricorn", 12, 22, 1, 19),
    ZodiacSign("Aquarius", 1, 20, 2, 18),
    ZodiacSign("Pisces", 2, 19, 3, 20),
    ZodiacSign("Aries", 3, 21, 4, 19),
    ZodiacSign("Taurus", 4, 20, 5, 20),
    ZodiacSign("Gemini", 5, 21, 6, 20),
    ZodiacSign("Cancer", 6, 21, 7, 22),
    ZodiacSign("Leo", 7, 23, 8, 22),
    ZodiacSign("Virgo", 8, 23, 9, 22),
    ZodiacSign("Libra", 9, 23, 10, 22),
    ZodiacSign("Scorpio", 10, 23, 11, 21),
    ZodiacSign("Sagittarius", 11, 22, 12, 21),
)


def _validate_date(value: datetime.date | str) -> datetime.date:
    """Validate and convert the input to a `datetime.date`."""
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            # Accept ISO format or common date formats.
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(f"String '{value}' is not a valid ISO date (YYYY-MM-DD).") from exc
    raise TypeError("date must be a datetime.date instance or an ISO format string.")


def get_zodiac_sign(date: datetime.date | str) -> ZodiacSign:
    """
    Return the zodiac sign for the given birth date.

    Parameters
    ----------
    date : datetime.date or str
        The birth date. If a string is provided, it must be in ISO format YYYY-MM-DD.

    Returns
    -------
    ZodiacSign
        The matching zodiac sign object.

    Raises
    ------
    ValueError
        If the input cannot be parsed into a valid date.
    """
    d = _validate_date(date)

    # Check Capricorn separately because its range wraps over year boundary.
    if (d.month == 12 and d.day >= 22) or (d.month == 1 and d.day <= 19):
        return ZodiacSign("Capricorn", 12, 22, 1, 19)

    for sign in _ZODIAC_SIGNS[1:]:
        if sign.contains(d.month, d.day):
            return sign

    # Fallback (should not happen)
    raise RuntimeError(f"Unable to determine zodiac sign for date {d.isoformat()}")


def get_all_signs() -> Tuple[str, ...]:
    """
    Return a tuple of all zodiac sign names in order.

    Returns
    -------
    tuple
        Names of the zodiac signs.
    """
    return tuple(sign.name for sign in _ZODIAC_SIGNS)


def is_valid_zodiac_name(name: str) -> bool:
    """Check if the provided name corresponds to a known zodiac sign."""
    return name.lower() in (s.lower() for s in get_all_signs())


def compare_birthdates(date1: datetime.date | str, date2: datetime.date | str) -> int:
    """
    Compare two birth dates and determine which falls earlier in the zodiac cycle.

    Parameters
    ----------
    date1 : datetime.date or str
        First birth date.
    date2 : datetime.date or str
        Second birth date.

    Returns
    -------
    int
        -1 if date1 precedes date2, 0 if same sign, 1 if after.

    Raises
    ------
    ValueError
        If any input cannot be parsed into a valid date.
    """
    d1 = _validate_date(date1)
    d2 = _validate_date(date2)

    s1 = get_zodiac_sign(d1).name
    s2 = get_zodiac_sign(d2).name

    order = list(get_all_signs())
    idx1, idx2 = order.index(s1), order.index(s2)
    if idx1 < idx2:
        return -1
    elif idx1 > idx2:
        return 1
    else:
        return 0


def signs_from_birthdates(dates: Iterable[datetime.date | str]) -> Tuple[ZodiacSign, ...]:
    """
    Convert an iterable of dates into their corresponding zodiac signs.

    Parameters
    ----------
    dates : iterable
        Collection of datetime.date or ISO format strings.

    Returns
    -------
    tuple
        ZodiacSign objects in the same order as input.
    """
    return tuple(get_zodiac_sign(d) for d in dates)


# Example usage: (removed from public API to keep module clean)
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m astro_mood.astrology YYYY-MM-DD")
        sys.exit(1)

    try:
        sign = get_zodiac_sign(sys.argv[1])
        print(f"Your zodiac sign is: {sign.name}")
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)