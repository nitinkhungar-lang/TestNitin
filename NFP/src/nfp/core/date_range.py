"""DateRange value object for NFP."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from nfp.core.exceptions import InvalidDateRangeError


@dataclass(frozen=True)
class DateRange:
    """Immutable date range [start, end] inclusive.

    Args:
        start: The start date (inclusive).
        end: The end date (inclusive).

    Raises:
        InvalidDateRangeError: If start > end.

    Example::

        fy = DateRange(date(2024, 4, 1), date(2025, 3, 31))
        assert fy.contains(date(2024, 10, 15))
        assert fy.days == 365
    """

    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise InvalidDateRangeError(
                f"DateRange start {self.start} must be <= end {self.end}"
            )

    def contains(self, d: date) -> bool:
        """Return True if d is within [start, end] inclusive."""
        return self.start <= d <= self.end

    def overlaps(self, other: "DateRange") -> bool:
        """Return True if this range overlaps with other."""
        return self.start <= other.end and other.start <= self.end

    @property
    def days(self) -> int:
        """Number of days in the range (end - start)."""
        return (self.end - self.start).days

    @classmethod
    def financial_year_india(cls, year: int) -> "DateRange":
        """Return the Indian financial year range (Apr 1 to Mar 31).

        Args:
            year: The starting year of the FY (e.g., 2024 for FY 2024-25).
        """
        return cls(date(year, 4, 1), date(year + 1, 3, 31))

    def __repr__(self) -> str:
        return f"DateRange({self.start}, {self.end})"
