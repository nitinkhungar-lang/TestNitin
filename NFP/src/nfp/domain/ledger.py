"""Ledger aggregate for NFP.

The Ledger is the explicit aggregate that owns the FinancialEvent stream.
ADR-008: Ledger assigns monotonic sequence numbers and provides replay.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from nfp.core.clock import Clock
from nfp.core.exceptions import LedgerSequenceError
from nfp.domain.financial_event import FinancialEvent


@dataclass
class Ledger:
    """Singleton aggregate that owns the immutable FinancialEvent stream.

    Responsibilities:
    - Accept appended events, assigning monotonic sequence numbers
    - Enforce sequence integrity (no gaps, no duplicates)
    - Track version for optimistic concurrency control

    The Ledger is a global singleton — there is exactly one per system.
    Sequence numbers are globally unique across all events.

    Note:
        The Ledger does NOT hold events in memory in production.
        In production, events are stored in the database and replayed
        via LedgerRepository. This in-memory list is for testing only.
    """

    id: UUID
    version: int                            # Incremented on each append
    last_sequence_number: int               # Last assigned sequence number
    created_at: datetime
    updated_at: datetime
    _events: list[FinancialEvent] = field(default_factory=list, repr=False, compare=False)

    def prepare_events(
        self,
        events: list[FinancialEvent],
        clock: Clock,
    ) -> list[FinancialEvent]:
        """Assign sequence numbers to a batch of events before persisting.

        This method is called by LedgerService before persisting events.
        It assigns sequence numbers starting from last_sequence_number + 1.
        It updates version and last_sequence_number on this aggregate.

        Args:
            events: Events to sequence. Must not yet have sequence numbers.
            clock: Clock for updating updated_at.

        Returns:
            New FinancialEvent instances with sequence_numbers assigned.

        Raises:
            LedgerSequenceError: If events list is empty.
        """
        if not events:
            raise LedgerSequenceError("Cannot append empty event list to Ledger")

        sequenced: list[FinancialEvent] = []
        next_seq = self.last_sequence_number + 1

        for event in events:
            # FinancialEvent is frozen, so we create a new instance with sequence_number set
            import dataclasses
            sequenced.append(dataclasses.replace(event, sequence_number=next_seq))
            next_seq += 1

        self.last_sequence_number = next_seq - 1
        self.version += 1
        self.updated_at = clock.now()
        return sequenced
