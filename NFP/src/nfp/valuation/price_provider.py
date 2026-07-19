"""Price Provider ABC."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class AssetValuation:
    price: Decimal

class PriceProvider(ABC):
    @abstractmethod
    def get_price(self, asset_id, date) -> AssetValuation:
        pass
