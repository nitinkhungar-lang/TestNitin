"""FinancialAccount domain entity for NFP."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from nfp.core.metadata import FdMetadata, LoanMetadata


@dataclass
class FinancialAccount:
    """A container for assets or cash — demat, savings, loan, etc.

    Examples:
    - Zerodha Demat (DEMAT)
    - HDFC Savings Primary (SAVINGS)
    - HDFC Home Loan (LOAN)

    Business Rules:
    - account_number is optional (privacy: store masked/partial only)
    - Closing an account requires zero balance
    - An account belongs to exactly one Institution
    """

    id: UUID
    account_type_code: str              # FK -> AccountType.code
    institution_id: UUID
    account_number: str | None          # Masked or partial
    name: str
    currency_code: str
    is_active: bool
    opened_date: date | None
    closed_date: date | None
    typed_metadata: LoanMetadata | FdMetadata | None
    created_at: datetime
    updated_at: datetime
    schema_version: int = 1
