"""Evidence domain entity for NFP.

Evidence represents original source documents.
Files are stored externally (Constitution C-evidence); only the
file_reference path and SHA-256 hash are stored in the database.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


EVIDENCE_TYPES = frozenset({
    "BROKER_CONTRACT_NOTE",
    "CAS",
    "BANK_STATEMENT",
    "SALARY_SLIP",
    "DIVIDEND_STATEMENT",
    "FD_RECEIPT",
    "BUILDER_DEMAND_LETTER",
    "LOAN_STATEMENT",
    "INSURANCE_RECEIPT",
    "TAX_FORM",
    "CORPORATE_ACTION_NOTICE",
    "MANUAL_ENTRY",
})


@dataclass
class Evidence:
    """An original source document that justifies a BusinessActivity.

    Immutability rules:
    - Evidence records are never modified
    - If a corrected document arrives, create a new Evidence with
      supersedes_id pointing to the old one
    - Every BusinessActivity must reference >= 1 Evidence

    File rules:
    - Files stored outside DB at NFP_EVIDENCE_ROOT (EvidenceFileStore)
    - file_hash is SHA-256 hex digest, verified on every retrieval
    """

    id: UUID
    evidence_type: str              # One of EVIDENCE_TYPES
    source_institution_id: UUID | None
    document_date: date
    received_date: date
    file_reference: str | None      # Relative path in evidence root
    file_hash: str | None           # SHA-256 hex
    file_size_bytes: int | None
    raw_content: str | None         # Extracted text
    version: int
    supersedes_id: UUID | None      # Points to evidence this corrects
    created_at: datetime
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.evidence_type not in EVIDENCE_TYPES:
            raise ValueError(
                f"Unknown evidence_type: {self.evidence_type!r}. Valid: {sorted(EVIDENCE_TYPES)}"
            )
        if self.version < 1:
            raise ValueError(f"Evidence version must be >= 1, got {self.version}")
