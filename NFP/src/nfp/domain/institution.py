"""Institution domain entity for NFP.

Institution is a first-class entity (ADR-008) with full lifecycle
management, unlike simple reference data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class InstitutionType(str, Enum):
    """Classification of a financial institution."""
    BROKER = "BROKER"
    BANK = "BANK"
    AMC = "AMC"
    INSURANCE = "INSURANCE"
    BUILDER = "BUILDER"
    DEPOSITORY = "DEPOSITORY"
    REGISTRAR = "REGISTRAR"
    EMPLOYER = "EMPLOYER"
    PENSION_FUND = "PENSION_FUND"
    EXCHANGE = "EXCHANGE"
    OTHER = "OTHER"


@dataclass
class Institution:
    """A financial institution with which the person has a relationship.

    Examples: Zerodha (BROKER), HDFC Bank (BANK), SBI MF (AMC), LIC (INSURANCE).

    Business Rules:
    - name must be unique within (institution_type, country_code)
    - Deactivating is non-destructive: existing accounts retain the link
    - regulatory_id format varies by type (SEBI, RBI, IRDAI)
    """

    id: UUID
    name: str
    institution_type: InstitutionType
    country_code: str
    website: str | None
    customer_care_email: str | None
    customer_care_phone: str | None
    regulatory_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    schema_version: int = 1

    def deactivate(self, updated_at: datetime) -> None:
        """Mark institution as inactive. Does not affect linked accounts.

        Args:
            updated_at: Timestamp of deactivation (from Clock).
        """
        self.is_active = False
        self.updated_at = updated_at

    def reactivate(self, updated_at: datetime) -> None:
        """Reactivate a previously deactivated institution.

        Args:
            updated_at: Timestamp of reactivation (from Clock).
        """
        self.is_active = True
        self.updated_at = updated_at
