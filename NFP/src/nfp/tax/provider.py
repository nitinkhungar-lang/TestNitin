"""Tax Rule Provider ABC."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HoldingPeriodRule:
    asset_types: List[str]
    long_term_threshold_months: int
    condition: Optional[str] = None

@dataclass
class TaxRate:
    rate: float

@dataclass
class TaxJurisdiction:
    code: str

class TaxRuleProvider(ABC):
    @abstractmethod
    def get_holding_period_rule(self, asset_type: str, acquisition_date) -> HoldingPeriodRule:
        pass
