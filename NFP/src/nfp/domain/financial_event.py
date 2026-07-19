"""FinancialEvent domain entity (immutable ledger record).

Constitution C1: FinancialEvents are NEVER modified or deleted.
Constitution C2: Append-only.

All mutations are enforced by:
1. @dataclass(frozen=True) — Python level
2. DB triggers — database level (see ADR-002)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from nfp.core.money import Money
from nfp.core.quantity import Quantity


@dataclass(frozen=True)
class FinancialEvent:
    """Atomic, immutable unit of the ledger.

    Never modified after creation. Corrections create reversal events.
    Created ONLY through EventGeneratorService, never directly.

    Attributes:
        id: Unique event identifier.
        ledger_id: FK to the Ledger aggregate.
        sequence_number: Global monotonic sequence — no gaps allowed.
        schema_version: For event schema evolution (ADR-013).
        event_type_code: FK to EventType reference data.
        business_activity_id: The activity that produced this event.
        account_id: The account this event affects.
        asset_id: The asset affected, if applicable.
        event_date: The date this event occurred.
        amount: Always positive. Direction indicates debit/credit.
        direction: 'DEBIT' or 'CREDIT'.
        quantity: Asset units affected, if applicable.
        description: Human-readable description.
        created_at: UTC timestamp when the record was created.
    """

    id: UUID
    ledger_id: UUID
    sequence_number: int
    schema_version: int
    event_type_code: str
    business_activity_id: UUID
    account_id: UUID
    asset_id: UUID | None
    event_date: date
    amount: Money
    direction: str              # "DEBIT" | "CREDIT"
    quantity: Quantity | None
    description: str
    created_at: datetime

    def __post_init__(self) -> None:
        if self.direction not in ("DEBIT", "CREDIT"):
            raise ValueError(f"FinancialEvent.direction must be DEBIT or CREDIT, got {self.direction!r}")
        if not self.amount.is_positive() and not self.amount.is_zero():
            raise ValueError(f"FinancialEvent.amount must be non-negative, got {self.amount}")
        if self.sequence_number < 1:
            raise ValueError(f"FinancialEvent.sequence_number must be >= 1, got {self.sequence_number}")
