"""Internal domain events for NFP.

Domain events are in-process pub/sub notifications distinct from
FinancialEvents (which are ledger records). They decouple modules
without tight coupling (Constitution C8: modular monolith).

Published via DomainEventBus — synchronous and in-process.
No external message broker is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from nfp.core.money import Money
from nfp.core.quantity import Quantity


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for all internal domain events."""
    event_id: UUID
    occurred_at: datetime
    schema_version: int = 1


@dataclass(frozen=True, kw_only=True)
class ActivityRecorded(DomainEvent):
    """Published when a BusinessActivity is confirmed."""
    activity_id: UUID
    activity_type_code: str
    activity_date: date


@dataclass(frozen=True, kw_only=True)
class FinancialEventAppended(DomainEvent):
    """Published when a FinancialEvent is appended to the Ledger."""
    financial_event_id: UUID
    sequence_number: int
    event_type_code: str
    business_activity_id: UUID


@dataclass(frozen=True, kw_only=True)
class LotCreated(DomainEvent):
    """Published when a new Lot is created by FifoEngine."""
    lot_id: UUID
    asset_id: UUID
    acquisition_date: date
    quantity: Quantity
    cost_per_unit: Money


@dataclass(frozen=True, kw_only=True)
class LotConsumed(DomainEvent):
    """Published when a Lot is fully or partially consumed."""
    lot_id: UUID
    asset_id: UUID
    quantity_consumed: Quantity
    remaining_quantity: Quantity
    sell_activity_id: UUID


@dataclass(frozen=True, kw_only=True)
class CorporateActionProcessed(DomainEvent):
    """Published after a CorporateAction adjusts Lots."""
    corporate_action_id: UUID
    asset_id: UUID
    action_type: str
    lots_adjusted: int


@dataclass(frozen=True, kw_only=True)
class EvidenceUploaded(DomainEvent):
    """Published when a new Evidence record is stored."""
    evidence_id: UUID
    evidence_type: str
    file_hash: str | None
