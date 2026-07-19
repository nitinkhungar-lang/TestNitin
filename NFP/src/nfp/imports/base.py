import abc
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal

from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.core.metadata import EquityCharges, MfCharges

@dataclass
class ParsedRecord:
    """A record parsed from an imported file, ready to be converted into a BusinessActivity."""
    activity_type_code: str
    activity_date: date
    settlement_date: Optional[date]
    description: str
    account_identifier: str  # Account name or code to look up
    asset_identifier: Optional[str]  # Asset ticker/ISIN to look up
    quantity: Optional[Quantity]
    price_per_unit: Optional[Money]
    total_amount: Money
    typed_charges: Union[EquityCharges, MfCharges, None] = None
    is_reversal: bool = False
    reverses_activity_id: Optional[str] = None
    status: str = "CONFIRMED"

class ImportParser(abc.ABC):
    """Abstract base class for all file import parsers."""

    @abc.abstractmethod
    def parse(self, file_content: str) -> List[ParsedRecord]:
        """Parse raw file content and return a list of ParsedRecords."""
        pass
