"""Lot domain entity for NFP.

Lot is a first-class domain entity (ADR-009), persisted in the database.
Represents a specific acquisition batch of an asset for FIFO tracking.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from nfp.core.exceptions import InsufficientLotQuantityError
from nfp.core.money import Money
from nfp.core.quantity import Quantity


class LotStatus(str, Enum):
    """Current consumption state of a Lot."""
    OPEN = "OPEN"                               # Full quantity available
    PARTIALLY_CONSUMED = "PARTIALLY_CONSUMED"   # Some quantity consumed
    CONSUMED = "CONSUMED"                       # Fully sold/disposed
    ADJUSTED = "ADJUSTED"                       # Modified by corporate action


@dataclass
class Lot:
    """A specific acquisition lot of an asset.

    Persisted as a domain entity (not a projection cache) because:
    1. FIFO state must survive application restarts
    2. Corporate actions adjust specific lots (CorporateAction aggregate)
    3. Lot history is part of the audit trail

    Lots are created by FifoEngine when ASSET_INCREASE events are processed.
    Lots are consumed when ASSET_DECREASE events are processed.

    Attributes:
        id: Unique lot identifier.
        asset_id: The asset this lot belongs to.
        account_id: The account holding this lot.
        acquisition_date: When the asset was acquired (determines FIFO order).
        original_quantity: How many units were originally acquired.
        remaining_quantity: How many units are still available.
        cost_per_unit: Acquisition cost per unit.
        status: Current LotStatus.
        source_activity_id: The BusinessActivity that created this lot.
        corporate_action_id: If created/adjusted by a CorporateAction.
        parent_lot_id: If this lot was split from a parent lot.
        created_at: UTC creation timestamp.
        updated_at: UTC last-update timestamp.
        schema_version: Schema version for evolution tracking.
    """

    id: UUID
    asset_id: UUID
    account_id: UUID
    acquisition_date: date
    original_quantity: Quantity
    remaining_quantity: Quantity
    cost_per_unit: Money
    status: LotStatus
    source_activity_id: UUID
    corporate_action_id: UUID | None
    parent_lot_id: UUID | None
    created_at: datetime
    updated_at: datetime
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.original_quantity.unit != self.remaining_quantity.unit:
            raise ValueError("original_quantity and remaining_quantity must have the same unit")
        if self.remaining_quantity > self.original_quantity:
            raise ValueError(
                f"remaining_quantity {self.remaining_quantity} cannot exceed "
                f"original_quantity {self.original_quantity}"
            )

    @property
    def total_cost(self) -> Money:
        """Total acquisition cost: cost_per_unit * original_quantity."""
        return Money(
            self.cost_per_unit.amount * self.original_quantity.value,
            self.cost_per_unit.currency_code,
        )

    @property
    def remaining_cost(self) -> Money:
        """Remaining cost: cost_per_unit * remaining_quantity."""
        return Money(
            self.cost_per_unit.amount * self.remaining_quantity.value,
            self.cost_per_unit.currency_code,
        )

    def consume(self, quantity: Quantity, updated_at: datetime) -> "LotConsumptionResult":
        """Consume a quantity from this lot.

        Updates this lot's remaining_quantity and status in-place.
        If only partially consumed, the lot status becomes PARTIALLY_CONSUMED.
        If fully consumed, the lot status becomes CONSUMED.

        Args:
            quantity: The quantity to consume.
            updated_at: UTC timestamp (from Clock.now()).

        Returns:
            LotConsumptionResult containing the consumed cost basis.

        Raises:
            InsufficientLotQuantityError: If quantity > remaining_quantity.
            UnitMismatchError: If quantity.unit != remaining_quantity.unit.
        """
        if quantity > self.remaining_quantity:
            raise InsufficientLotQuantityError(
                str(self.remaining_quantity),
                str(quantity),
            )
        new_remaining = self.remaining_quantity - quantity
        consumed_cost = Money(
            self.cost_per_unit.amount * quantity.value,
            self.cost_per_unit.currency_code,
        )
        self.remaining_quantity = new_remaining
        self.updated_at = updated_at
        if new_remaining.is_zero():
            self.status = LotStatus.CONSUMED
        else:
            self.status = LotStatus.PARTIALLY_CONSUMED
        return LotConsumptionResult(
            lot_id=self.id,
            quantity_consumed=quantity,
            cost_consumed=consumed_cost,
            cost_per_unit=self.cost_per_unit,
            acquisition_date=self.acquisition_date,
        )

    def apply_split(self, quantity_multiplier: Decimal, price_divisor: Decimal, updated_at: datetime) -> None:
        """Apply a stock split or bonus: multiply quantity, divide cost_per_unit.

        Args:
            quantity_multiplier: Factor to multiply quantities by (e.g., 2 for 2:1 split).
            price_divisor: Factor to divide cost_per_unit by (same value as multiplier).
            updated_at: UTC timestamp (from Clock.now()).
        """
        self.original_quantity = Quantity(
            self.original_quantity.value * quantity_multiplier,
            self.original_quantity.unit,
        )
        self.remaining_quantity = Quantity(
            self.remaining_quantity.value * quantity_multiplier,
            self.remaining_quantity.unit,
        )
        self.cost_per_unit = Money(
            self.cost_per_unit.amount / price_divisor,
            self.cost_per_unit.currency_code,
        )
        self.status = LotStatus.ADJUSTED
        self.updated_at = updated_at


@dataclass(frozen=True)
class LotConsumptionResult:
    """Result of consuming quantity from a Lot.

    Returned by Lot.consume() and used by FifoEngine to compute capital gains.
    """
    lot_id: UUID
    quantity_consumed: Quantity
    cost_consumed: Money
    cost_per_unit: Money
    acquisition_date: date
