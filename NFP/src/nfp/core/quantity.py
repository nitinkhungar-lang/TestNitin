"""Quantity value object for NFP.

Represents a counted amount of an asset (units, grams, sq ft, NAV units).
Like Money, always uses Decimal and is immutable.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from nfp.core.exceptions import InvalidQuantityError, UnitMismatchError

_VALID_UNITS = frozenset({"UNITS", "GRAMS", "SQ_FT", "NAV_UNITS"})


@dataclass(frozen=True)
class Quantity:
    """Immutable quantity of an asset with a unit.

    Args:
        value: The quantity as Decimal.
        unit: One of 'UNITS', 'GRAMS', 'SQ_FT', 'NAV_UNITS'.

    Raises:
        InvalidQuantityError: If value is not a Decimal.
        UnitMismatchError: If arithmetic between different units is attempted.

    Example::

        qty = Quantity(Decimal('100'), 'UNITS')
        sold = Quantity(Decimal('75'), 'UNITS')
        remaining = qty - sold  # Quantity(Decimal('25'), 'UNITS')
    """

    value: Decimal
    unit: str = "UNITS"

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            raise InvalidQuantityError(
                f"Quantity.value must be Decimal, got {type(self.value).__name__}"
            )
        if self.unit not in _VALID_UNITS:
            raise InvalidQuantityError(f"Invalid Quantity unit: {self.unit!r}. Valid: {_VALID_UNITS}")

    def __add__(self, other: object) -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_unit(other)
        return Quantity(self.value + other.value, self.unit)

    def __sub__(self, other: object) -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_unit(other)
        return Quantity(self.value - other.value, self.unit)

    def __mul__(self, factor: object) -> "Quantity":
        if not isinstance(factor, Decimal):
            raise InvalidQuantityError(f"Quantity multiply factor must be Decimal, got {type(factor).__name__}")
        return Quantity(self.value * factor, self.unit)

    def __truediv__(self, divisor: object) -> "Quantity":
        if not isinstance(divisor, Decimal):
            raise InvalidQuantityError(f"Quantity divisor must be Decimal, got {type(divisor).__name__}")
        if divisor == Decimal("0"):
            raise ZeroDivisionError("Cannot divide Quantity by zero")
        return Quantity(self.value / divisor, self.unit)

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.unit)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_unit(other)
        return self.value < other.value

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_unit(other)
        return self.value <= other.value

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_unit(other)
        return self.value > other.value

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_unit(other)
        return self.value >= other.value

    def _check_unit(self, other: "Quantity") -> None:
        if self.unit != other.unit:
            raise UnitMismatchError(self.unit, other.unit)

    def is_positive(self) -> bool:
        """Return True if value > 0."""
        return self.value > Decimal("0")

    def is_zero(self) -> bool:
        """Return True if value == 0."""
        return self.value == Decimal("0")

    def is_negative(self) -> bool:
        """Return True if value < 0."""
        return self.value < Decimal("0")

    def __repr__(self) -> str:
        return f"Quantity({self.value!r}, {self.unit!r})"

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"
