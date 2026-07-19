"""Asset domain entity for NFP."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from nfp.core.metadata import FdMetadata, LoanMetadata, RealEstateMetadata


@dataclass
class Asset:
    """A financial instrument or asset that can be owned.

    Examples: RELIANCE equity, HDFC Top 100 MF, HDFC FD, Flat in Mumbai.

    Business Rules:
    - ISIN is unique when present
    - (symbol, exchange) is unique when both present
    - For corporate actions, a new BusinessActivity adjusts quantity/cost of existing Lots
    """

    id: UUID
    asset_type_code: str                   # FK -> AssetType.code
    symbol: str | None
    isin: str | None
    name: str
    currency_code: str
    exchange: str | None                    # "NSE", "BSE", "NASDAQ"
    institution_id: UUID | None            # For FDs, loans — issuing institution
    typed_metadata: FdMetadata | RealEstateMetadata | LoanMetadata | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    schema_version: int = 1
