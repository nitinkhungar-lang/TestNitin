"""Validation rules for FinancialEvent and BusinessActivity."""
from nfp.domain.financial_event import FinancialEvent

class ValidationRule:
    def validate(self, event: FinancialEvent) -> None:
        if event.amount.amount < 0:
            raise ValueError("Event amount cannot be negative")
