"""Money value object and CurrencyRegistry for NFP.

Constitution C3: All monetary values use Decimal — never float.
Constitution C12: Rounding always uses CurrencyRegistry.decimal_places.

All arithmetic between different currencies raises CurrencyMismatchError.
Currency conversion must go through ExchangeRate explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from nfp.core.exceptions import CurrencyMismatchError, CurrencyNotFoundError, InvalidMoneyError

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Money:
    """Immutable monetary value with currency.

    Always uses Decimal — never float. Arithmetic between different currencies
    raises CurrencyMismatchError (Constitution C3).

    Args:
        amount: The monetary amount as Decimal.
        currency_code: ISO 4217 currency code (e.g., 'INR', 'USD').

    Raises:
        InvalidMoneyError: If amount is not a Decimal instance.

    Example::

        price = Money(Decimal('2500.00'), 'INR')
        tax = Money(Decimal('25.00'), 'INR')
        total = price + tax  # Money(Decimal('2525.00'), 'INR')
    """

    amount: Decimal
    currency_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise InvalidMoneyError(
                f"Money.amount must be Decimal, got {type(self.amount).__name__}"
            )
        if not self.currency_code or not self.currency_code.strip():
            raise InvalidMoneyError("Money.currency_code cannot be empty")

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return Money(self.amount + other.amount, self.currency_code)

    def __sub__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency_code)

    def __mul__(self, factor: object) -> "Money":
        if not isinstance(factor, Decimal):
            raise InvalidMoneyError(f"Money multiply factor must be Decimal, got {type(factor).__name__}")
        return Money(self.amount * factor, self.currency_code)

    def __truediv__(self, divisor: object) -> "Money":
        if not isinstance(divisor, Decimal):
            raise InvalidMoneyError(f"Money divisor must be Decimal, got {type(divisor).__name__}")
        if divisor == Decimal("0"):
            raise ZeroDivisionError("Cannot divide Money by zero")
        return Money(self.amount / divisor, self.currency_code)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency_code)

    def __abs__(self) -> "Money":
        return Money(abs(self.amount), self.currency_code)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return self.amount < other.amount

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        self._check_currency(other)
        return self.amount >= other.amount

    def _check_currency(self, other: "Money") -> None:
        if self.currency_code != other.currency_code:
            raise CurrencyMismatchError(self.currency_code, other.currency_code)

    def round(self, registry: "CurrencyRegistry") -> "Money":
        """Round to this currency's standard decimal places using ROUND_HALF_UP.

        Constitution C12: Always use CurrencyRegistry, never hardcode decimal places.

        Args:
            registry: CurrencyRegistry to look up decimal_places.

        Returns:
            New Money rounded to the currency's standard precision.
        """
        places = registry.get(self.currency_code).decimal_places
        return self.round_to(places)

    def round_to(self, places: int) -> "Money":
        """Round to a specific number of decimal places using ROUND_HALF_UP.

        Prefer round(registry) over this method unless places is dynamic.

        Args:
            places: Number of decimal places.

        Returns:
            New Money rounded to the specified precision.
        """
        quantizer = Decimal(10) ** -places
        return Money(
            self.amount.quantize(quantizer, rounding=ROUND_HALF_UP),
            self.currency_code,
        )

    def is_positive(self) -> bool:
        """Return True if amount > 0."""
        return self.amount > Decimal("0")

    def is_negative(self) -> bool:
        """Return True if amount < 0."""
        return self.amount < Decimal("0")

    def is_zero(self) -> bool:
        """Return True if amount == 0."""
        return self.amount == Decimal("0")

    def __repr__(self) -> str:
        return f"Money({self.amount!r}, {self.currency_code!r})"

    def __str__(self) -> str:
        return f"{self.currency_code} {self.amount}"


@dataclass(frozen=True)
class CurrencyInfo:
    """Currency information used by CurrencyRegistry."""

    code: str
    name: str
    symbol: str
    decimal_places: int
    is_active: bool = True


class CurrencyRegistry:
    """Registry of currencies. Provides lookup for monetary rounding.

    Loaded from reference data at bootstrap. Injected wherever
    Money.round() is called (Constitution C12).

    Example::

        registry = CurrencyRegistry()
        registry.register(CurrencyInfo('INR', 'Indian Rupee', '\u20b9', 2))
        inr = registry.get('INR')  # CurrencyInfo
        price = Money(Decimal('99.999'), 'INR').round(registry)  # INR 100.00
    """

    def __init__(self) -> None:
        self._currencies: dict[str, CurrencyInfo] = {}

    def register(self, currency: CurrencyInfo) -> None:
        """Register a currency in the registry.

        Args:
            currency: The CurrencyInfo to register.
        """
        self._currencies[currency.code] = currency

    def get(self, code: str) -> CurrencyInfo:
        """Get a currency by its ISO 4217 code.

        Args:
            code: ISO 4217 currency code (e.g., 'INR').

        Returns:
            The CurrencyInfo for the given code.

        Raises:
            CurrencyNotFoundError: If the code is not registered.
        """
        try:
            return self._currencies[code]
        except KeyError:
            raise CurrencyNotFoundError(code)

    def all_active(self) -> list[CurrencyInfo]:
        """Return all active currencies."""
        return [c for c in self._currencies.values() if c.is_active]

    @classmethod
    def with_defaults(cls) -> "CurrencyRegistry":
        """Create a registry pre-loaded with the standard NFP currencies."""
        registry = cls()
        defaults = [
            CurrencyInfo("INR", "Indian Rupee", "\u20b9", 2),
            CurrencyInfo("USD", "US Dollar", "$", 2),
            CurrencyInfo("EUR", "Euro", "\u20ac", 2),
            CurrencyInfo("GBP", "British Pound", "\u00a3", 2),
            CurrencyInfo("JPY", "Japanese Yen", "\u00a5", 0),
            CurrencyInfo("SGD", "Singapore Dollar", "S$", 2),
            CurrencyInfo("AED", "UAE Dirham", "AED", 2),
            CurrencyInfo("CAD", "Canadian Dollar", "C$", 2),
            CurrencyInfo("AUD", "Australian Dollar", "A$", 2),
            CurrencyInfo("CHF", "Swiss Franc", "CHF", 2),
        ]
        for c in defaults:
            registry.register(c)
        return registry
