"""BusinessActivity aggregate root for NFP.

BusinessActivity is the primary aggregate root. It owns its
FinancialEvents (via the Ledger) and references Evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID

from nfp.core.exceptions import EvidenceRequiredError
from nfp.core.metadata import EquityCharges, MfCharges
from nfp.core.money import Money
from nfp.core.quantity import Quantity


ACTIVITY_STATUSES = frozenset({"CONFIRMED", "PENDING", "REVERSED"})


@dataclass
class BusinessActivity:
    """A real-world financial action taken by the person.

    BusinessActivity is the primary aggregate root. It:
    - References one or more Evidence records
    - Generates FinancialEvents through EventGeneratorService
    - Is linked to a FinancialAccount and optionally an Asset

    Business Rules:
    - Must reference at least one Evidence (EvidenceRequiredError)
    - Reversals link back to the original via reverses_activity_id
    - typed_charges replaces untyped dict metadata
    """

    id: UUID
    activity_type_code: str             # FK -> ActivityType.code (reference data)
    activity_date: date
    settlement_date: date | None
    description: str
    evidence_ids: list[UUID]
    account_id: UUID
    asset_id: UUID | None
    quantity: Quantity | None
    price_per_unit: Money | None
    total_amount: Money
    typed_charges: EquityCharges | MfCharges | None
    is_reversal: bool
    reverses_activity_id: UUID | None
    status: str
    created_at: datetime
    schema_version: int = 1

    def __post_init__(self) -> None:
        if not self.evidence_ids:
            raise EvidenceRequiredError(
                f"BusinessActivity {self.id} must reference at least one Evidence"
            )
        if self.status not in ACTIVITY_STATUSES:
            raise ValueError(f"Invalid status: {self.status!r}. Valid: {ACTIVITY_STATUSES}")
        if self.settlement_date is not None and self.settlement_date < self.activity_date:
            raise ValueError(
                f"settlement_date {self.settlement_date} must be >= activity_date {self.activity_date}"
            )

    def mark_reversed(self) -> None:
        """Mark this activity as reversed. Called when a reversal activity is created."""
        self.status = "REVERSED"
