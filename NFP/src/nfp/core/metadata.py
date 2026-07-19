"""Typed metadata value objects for NFP domain entities.

Replaces untyped dict metadata with strongly-typed value objects.
Each asset type and activity type has its own typed metadata.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nfp.core.money import Money


@dataclass(frozen=True)
class FdMetadata:
    """Metadata for a Fixed Deposit asset.

    Args:
        maturity_date: When the FD matures.
        annual_interest_rate: Interest rate as percentage (e.g., Decimal('7.25') for 7.25%).
        compounding: Compounding frequency: 'QUARTERLY', 'MONTHLY', 'ANNUALLY', 'SIMPLE'.
        auto_renewal: Whether the FD auto-renews on maturity.
    """

    maturity_date: date
    annual_interest_rate: Decimal
    compounding: str
    auto_renewal: bool = False

    def __post_init__(self) -> None:
        valid_compounding = {"QUARTERLY", "MONTHLY", "ANNUALLY", "SIMPLE"}
        if self.compounding not in valid_compounding:
            raise ValueError(f"Invalid compounding: {self.compounding!r}. Valid: {valid_compounding}")
        if self.annual_interest_rate <= Decimal("0"):
            raise ValueError(f"FD interest rate must be positive, got {self.annual_interest_rate}")


@dataclass(frozen=True)
class RealEstateMetadata:
    """Metadata for a Real Estate asset."""

    address_line1: str
    city: str
    state: str
    pin_code: str
    property_type: str          # 'FLAT' | 'VILLA' | 'PLOT' | 'COMMERCIAL'
    address_line2: str | None = None
    area_sq_ft: Decimal | None = None
    builder_name: str | None = None

    def __post_init__(self) -> None:
        valid_types = {"FLAT", "VILLA", "PLOT", "COMMERCIAL"}
        if self.property_type not in valid_types:
            raise ValueError(f"Invalid property_type: {self.property_type!r}. Valid: {valid_types}")


@dataclass(frozen=True)
class LoanMetadata:
    """Metadata for a Loan account."""

    principal_amount_value: Decimal
    principal_amount_currency: str
    annual_interest_rate: Decimal
    tenure_months: int
    emi_start_date: date
    loan_type: str              # 'HOME' | 'PERSONAL' | 'VEHICLE' | 'EDUCATION'

    def __post_init__(self) -> None:
        valid_types = {"HOME", "PERSONAL", "VEHICLE", "EDUCATION"}
        if self.loan_type not in valid_types:
            raise ValueError(f"Invalid loan_type: {self.loan_type!r}. Valid: {valid_types}")
        if self.tenure_months <= 0:
            raise ValueError(f"Loan tenure_months must be positive, got {self.tenure_months}")


@dataclass(frozen=True)
class EquityCharges:
    """Charges associated with an equity buy or sell activity.

    All fields are Money values in the same currency.

    Example::

        charges = EquityCharges(
            brokerage=Money(Decimal('0'), 'INR'),
            stt=Money(Decimal('25.00'), 'INR'),
            exchange_fee=Money(Decimal('8.63'), 'INR'),
            sebi_fee=Money(Decimal('0.25'), 'INR'),
            gst=Money(Decimal('1.55'), 'INR'),
            stamp_duty=Money(Decimal('37.50'), 'INR'),
        )
        total = charges.total  # Money(Decimal('72.93'), 'INR')
    """

    brokerage: "Money"
    stt: "Money"
    exchange_fee: "Money"
    sebi_fee: "Money"
    gst: "Money"
    stamp_duty: "Money"

    @property
    def total(self) -> "Money":
        """Sum of all charges. All must be in the same currency."""
        return self.brokerage + self.stt + self.exchange_fee + self.sebi_fee + self.gst + self.stamp_duty


@dataclass(frozen=True)
class MfCharges:
    """Charges for mutual fund buy or sell activities."""

    stamp_duty: "Money"
    exit_load: "Money | None" = None
    stt: "Money | None" = None

    @property
    def total(self) -> "Money":
        """Sum of all non-None charges."""
        total = self.stamp_duty
        if self.exit_load is not None:
            total = total + self.exit_load
        if self.stt is not None:
            total = total + self.stt
        return total


@dataclass(frozen=True)
class SplitRatio:
    """Corporate action split or consolidation ratio.

    Example — 2:1 stock split (each share becomes 2 shares)::

        ratio = SplitRatio(old_face_value=Decimal('10'), new_face_value=Decimal('5'), numerator=2, denominator=1)
        # quantity_multiplier = 2 (double the shares)
        # price_divisor = 2 (halve the price)
    """

    old_face_value: Decimal
    new_face_value: Decimal
    numerator: int      # New shares received per 1 old share
    denominator: int = 1

    def __post_init__(self) -> None:
        if self.numerator <= 0 or self.denominator <= 0:
            raise ValueError("SplitRatio numerator and denominator must be positive")

    @property
    def quantity_multiplier(self) -> Decimal:
        """Factor by which existing lot quantity is multiplied."""
        return Decimal(self.numerator) / Decimal(self.denominator)

    @property
    def price_divisor(self) -> Decimal:
        """Factor by which cost_per_unit is divided to maintain total cost."""
        return Decimal(self.numerator) / Decimal(self.denominator)
