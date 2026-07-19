"""MarketPrice aggregate for NFP."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from nfp.core.money import Money
from uuid import UUID

@dataclass(frozen=True)
class MarketPrice:
    asset_id: UUID
    date: date
    price: Money
    source: str
