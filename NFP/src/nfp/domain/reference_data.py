"""Reference data domain objects for NFP.

These are immutable value-like objects seeded at bootstrap and loaded
from reference-data/ JSON files. They are not Entities (no mutable state).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    """ISO 4217 currency."""
    code: str
    name: str
    symbol: str
    decimal_places: int
    is_active: bool = True


@dataclass(frozen=True)
class Country:
    """ISO 3166-1 alpha-2 country."""
    code: str
    name: str
    currency_code: str


@dataclass(frozen=True)
class AssetType:
    """Type classification for an Asset."""
    code: str
    name: str
    country_code: str | None = None


@dataclass(frozen=True)
class AccountType:
    """Type classification for a FinancialAccount."""
    code: str
    name: str


@dataclass(frozen=True)
class EventType:
    """Type classification for a FinancialEvent."""
    code: str
    name: str
    direction: str    # "DEBIT" | "CREDIT" | "BOTH"
    category: str     # "CASH" | "ASSET" | "EXPENSE" | "INCOME" | "TAX" | "LIABILITY" | "REVERSAL"


@dataclass(frozen=True)
class ActivityType:
    """Type classification for a BusinessActivity.

    Stored as versioned reference data (not a Python enum) so new types
    can be added via data migration without code changes.
    """
    code: str
    name: str
    category: str           # "EQUITY" | "MF" | "FIXED_INCOME" | "REAL_ESTATE" | "LOANS" | "BANKING" | "GENERAL"
    description: str
    event_template_key: str
    is_active: bool = True
    schema_version: int = 1
