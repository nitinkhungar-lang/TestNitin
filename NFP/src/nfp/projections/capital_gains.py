"""Capital Gain Projection."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

@dataclass
class CapitalGainProjection:
    asset_id: UUID
    sell_date: date
    buy_date: date
    quantity: Decimal
    sell_value: Decimal
    buy_value: Decimal
    currency: str
    
    @property
    def amount(self) -> float:
        return float(self.sell_value - self.buy_value)
