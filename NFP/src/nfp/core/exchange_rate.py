"""ExchangeRate value object for NFP."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from nfp.core.exceptions import CurrencyMismatchError
from nfp.core.money import Money


@dataclass(frozen=True)
class ExchangeRate:
    """Immutable exchange rate between two currencies on a specific date.

    Args:
        from_currency: Source currency ISO code (e.g., 'USD').
        to_currency: Target currency ISO code (e.g., 'INR').
        rate: Conversion rate as Decimal (always positive).
        effective_date: The date for which this rate is valid.
        source: Where this rate came from: 'RBI', 'MANUAL', 'OANDA', etc.

    Example::

        rate = ExchangeRate('USD', 'INR', Decimal('83.50'), date(2024, 1, 15), 'RBI')
        inr_amount = rate.convert(Money(Decimal('100'), 'USD'))  # INR 8350.00
    """

    from_currency: str
    to_currency: str
    rate: Decimal
    effective_date: date
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.rate, Decimal):
            raise TypeError(f"ExchangeRate.rate must be Decimal, got {type(self.rate).__name__}")
        if self.rate <= Decimal("0"):
            raise ValueError(f"ExchangeRate.rate must be positive, got {self.rate}")

    def convert(self, money: Money) -> Money:
        """Convert money from from_currency to to_currency.

        Args:
            money: Money in from_currency.

        Returns:
            Equivalent Money in to_currency.

        Raises:
            CurrencyMismatchError: If money.currency_code != from_currency.
        """
        if money.currency_code != self.from_currency:
            raise CurrencyMismatchError(money.currency_code, self.from_currency)
        return Money(money.amount * self.rate, self.to_currency)

    def inverse(self) -> "ExchangeRate":
        """Return the inverse rate (to_currency → from_currency)."""
        return ExchangeRate(
            from_currency=self.to_currency,
            to_currency=self.from_currency,
            rate=Decimal("1") / self.rate,
            effective_date=self.effective_date,
            source=self.source,
        )

    def __repr__(self) -> str:
        return (
            f"ExchangeRate({self.from_currency}/{self.to_currency}, "
            f"{self.rate}, {self.effective_date})"
        )
