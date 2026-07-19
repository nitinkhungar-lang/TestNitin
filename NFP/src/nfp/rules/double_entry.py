"""Double Entry Validator."""
from typing import List
from nfp.domain.financial_event import FinancialEvent

class DoubleEntryValidator:
    def validate(self, events: List[FinancialEvent]) -> bool:
        return True
