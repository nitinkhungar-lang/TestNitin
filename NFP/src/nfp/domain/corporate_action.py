"""CorporateAction aggregate for NFP.

CorporateAction is a separate aggregate from BusinessActivity (ADR-010).
It adjusts existing Lots when corporate events occur.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from nfp.core.clock import Clock
from nfp.core.metadata import SplitRatio
from nfp.domain.lot import Lot, LotStatus


class CorporateActionType(str, Enum):
    """Type of corporate action."""
    SPLIT = "SPLIT"
    BONUS = "BONUS"
    CONSOLIDATION = "CONSOLIDATION"
    MERGER = "MERGER"
    SPINOFF = "SPINOFF"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"


@dataclass
class CorporateAction:
    """An aggregate representing a corporate action that adjusts Lots.

    Corporate actions operate on Lots, not on BusinessActivities, because:
    - They affect all existing lots of an asset simultaneously
    - They change quantity/price of past acquisitions retroactively
    - They must preserve original acquisition dates (for capital gains)

    After applying a CorporateAction, a CorporateActionProcessed
    domain event is emitted.
    """

    id: UUID
    asset_id: UUID
    action_type: CorporateActionType
    record_date: date
    effective_date: date
    split_ratio: SplitRatio | None     # For SPLIT, CONSOLIDATION, BONUS
    new_asset_id: UUID | None          # For MERGER, SPINOFF: resulting asset
    exchange_ratio: object | None      # Decimal: shares of new per share of old
    description: str
    evidence_ids: list[UUID]
    created_at: datetime
    schema_version: int = 1

    def apply_to_lots(self, lots: list[Lot], clock: Clock) -> list[Lot]:
        """Apply this corporate action to the given lots.

        Modifies the lots in-place and returns them.

        For SPLIT/BONUS: multiplies remaining_quantity, divides cost_per_unit.
        For CONSOLIDATION: divides remaining_quantity, multiplies cost_per_unit.
        For MERGER: marks old lots CONSUMED (new lots created separately).

        Args:
            lots: Open/partial lots for asset_id that need adjustment.
            clock: Clock for setting updated_at.

        Returns:
            The modified lots list.
        """
        now = clock.now()
        if self.action_type in (CorporateActionType.SPLIT, CorporateActionType.BONUS):
            if self.split_ratio is None:
                raise ValueError(f"split_ratio required for {self.action_type}")
            for lot in lots:
                if lot.status not in (LotStatus.CONSUMED,):
                    lot.apply_split(
                        quantity_multiplier=self.split_ratio.quantity_multiplier,
                        price_divisor=self.split_ratio.price_divisor,
                        updated_at=now,
                    )
        elif self.action_type == CorporateActionType.CONSOLIDATION:
            if self.split_ratio is None:
                raise ValueError("split_ratio required for CONSOLIDATION")
            for lot in lots:
                if lot.status not in (LotStatus.CONSUMED,):
                    # Inverse: divide quantity, multiply price
                    from decimal import Decimal
                    multiplier = Decimal(self.split_ratio.denominator) / Decimal(self.split_ratio.numerator)
                    lot.apply_split(
                        quantity_multiplier=multiplier,
                        price_divisor=multiplier,
                        updated_at=now,
                    )
        elif self.action_type == CorporateActionType.MERGER:
            for lot in lots:
                lot.status = LotStatus.CONSUMED
                lot.updated_at = now
        return lots
