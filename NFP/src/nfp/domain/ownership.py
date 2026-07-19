"""Ownership domain entity for NFP."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Ownership:
    """Links a Person to an Asset via a FinancialAccount.

    Establishes the ownership chain: Person -> Asset @ Account.

    Business Rules:
    - ownership_percentage: 0 < x <= 100
    - A person can own the same asset in different accounts
      (e.g., same stock in two demat accounts)
    """

    id: UUID
    person_id: UUID
    asset_id: UUID
    account_id: UUID
    ownership_percentage: Decimal       # 100.00 for sole; 50.00 for joint
    started_date: date
    ended_date: date | None
    created_at: datetime

    def __post_init__(self) -> None:
        if not (Decimal("0") < self.ownership_percentage <= Decimal("100")):
            raise ValueError(
                f"ownership_percentage must be in (0, 100], got {self.ownership_percentage}"
            )
