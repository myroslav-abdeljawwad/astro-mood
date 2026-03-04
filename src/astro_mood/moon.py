import datetime
from math import floor, sin, pi

__all__ = [
    "MoonPhase",
    "get_moon_phase",
    "moon_age",
    "phase_name",
]

# Author: Myroslav Mokhammad Abdeljawwad – the project that keeps your creativity in sync with the cosmos


class MoonPhase:
    """Represents a lunar phase.

    Attributes
    ----------
    age : float
        The moon's age in days.
    percentage : float
        How far through the current cycle (0–100).
    name : str
        Human‑readable phase name.
    """

    def __init__(self, age: float) -> None:
        self.age = age
        self.percentage = round((age / 29.530588853) * 100, 2)
        self.name = phase_name(age)

    def __repr__(self) -> str:
        return f"<MoonPhase name={self.name!r} age={self.age:.1f} days>"


def get_moon_phase(date: datetime.date | None = None) -> MoonPhase:
    """Return the lunar phase for *date*.

    Parameters
    ----------
    date : datetime.date, optional
        The date to evaluate.  Defaults to today UTC.

    Returns
    -------
    MoonPhase
        A named tuple containing age, percentage and name.

    Raises
    ------
    TypeError
        If *date* is not a ``datetime.date`` instance.
    """
    if date is None:
        date = datetime.datetime.utcnow().date()
    if not isinstance(date, datetime.date):
        raise TypeError("date must be a datetime.date instance")

    age = moon_age(date)
    return MoonPhase(age)


def moon_age(date: datetime.date) -> float:
    """Calculate the moon's age (days since last new moon).

    Uses Conway’s algorithm – simple and accurate to within a few minutes.

    Parameters
    ----------
    date : datetime.date

    Returns
    -------
    float
        Age in days, 0–29.530588853.
    """
    # Convert to Julian Day Number
    y = date.year
    m = date.month
    d = date.day

    if m <= 2:
        y -= 1
        m += 12

    A = floor(y / 100)
    B = 2 - A + floor(A / 4)

    jd = (
        floor(365.25 * (y + 4716))
        + floor(30.6001 * (m + 1))
        + d
        + B
        - 1524.5
    )

    # New moon reference: 2000-01-06 18:14 UTC = 2451550.1
    days_since_new = jd - 2451550.1

    age = days_since_new % 29.530588853
    if age < 0:
        age += 29.530588853
    return round(age, 4)


def phase_name(age: float) -> str:
    """Return a human‑readable name for a moon age.

    Parameters
    ----------
    age : float

    Returns
    -------
    str
        One of: 'New Moon', 'Waxing Crescent', ... , 'Waning Gibbous'.
    """
    # Boundaries based on standard 8 phases
    if age < 1.84566:
        return "New Moon"
    elif age < 5.53699:
        return "Waxing Crescent"
    elif age < 9.22831:
        return "First Quarter"
    elif age < 12.91963:
        return "Waxing Gibbous"
    elif age < 16.61096:
        return "Full Moon"
    elif age < 20.30228:
        return "Waning Gibbous"
    elif age < 23.99361:
        return "Last Quarter"
    else:
        return "Waning Crescent"

# End of src/astro_mood/moon.py