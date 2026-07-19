"""Clock abstraction for NFP.

Constitution C11: Never call datetime.now() or date.today() directly
in domain or service code. Always inject a Clock instance.

Usage::

    # In production:
    clock = SystemClock()
    
    # In tests:
    clock = FixedClock(date(2024, 1, 15))
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, date, datetime


class Clock(ABC):
    """Abstraction for current time. Enables deterministic testing."""

    @abstractmethod
    def today(self) -> date:
        """Return the current date."""
        ...

    @abstractmethod
    def now(self) -> datetime:
        """Return the current UTC datetime."""
        ...


class SystemClock(Clock):
    """Production clock that delegates to the system time."""

    def today(self) -> date:
        """Return today's date from the system clock."""
        return date.today()

    def now(self) -> datetime:
        """Return the current UTC datetime from the system clock."""
        return datetime.now(UTC)


class FixedClock(Clock):
    """Test clock that returns a fixed date and time for deterministic tests.

    Args:
        fixed_date: The date to always return from today().
        fixed_datetime: The datetime to always return from now().
            If None, defaults to midnight UTC on fixed_date.

    Example::

        clock = FixedClock(date(2024, 6, 1))
        assert clock.today() == date(2024, 6, 1)
    """

    def __init__(
        self,
        fixed_date: date,
        fixed_datetime: datetime | None = None,
    ) -> None:
        self._date = fixed_date
        self._datetime = fixed_datetime or datetime(
            fixed_date.year,
            fixed_date.month,
            fixed_date.day,
            tzinfo=UTC,
        )

    def today(self) -> date:
        """Return the fixed date."""
        return self._date

    def now(self) -> datetime:
        """Return the fixed datetime."""
        return self._datetime
