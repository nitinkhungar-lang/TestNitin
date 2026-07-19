"""NFP custom exceptions hierarchy.

All NFP exceptions inherit from NFPError.
Constitution rules enforced through exceptions:
- CurrencyMismatchError: Constitution C3 (Decimal for money)
- LedgerMutationError: Constitution C1 (Immutable ledger)
"""
from __future__ import annotations


class NFPError(Exception):
    """Base class for all NFP exceptions."""


# --- Value Object Errors ---

class CurrencyMismatchError(NFPError):
    """Raised when Money arithmetic is attempted between different currencies."""
    def __init__(self, left: str, right: str) -> None:
        super().__init__(f"Currency mismatch: cannot operate on {left} and {right}")
        self.left = left
        self.right = right


class UnitMismatchError(NFPError):
    """Raised when Quantity arithmetic is attempted between different units."""
    def __init__(self, left: str, right: str) -> None:
        super().__init__(f"Unit mismatch: cannot operate on {left} and {right}")


class InvalidMoneyError(NFPError):
    """Raised when Money is constructed with a non-Decimal amount."""


class InvalidQuantityError(NFPError):
    """Raised when Quantity is constructed with a non-Decimal value."""


class InvalidPanError(NFPError):
    """Raised when a PAN string does not match the required format."""


class InvalidDateRangeError(NFPError):
    """Raised when a DateRange has start > end."""


# --- Ledger Errors ---

class LedgerMutationError(NFPError):
    """Raised when an attempt is made to mutate an immutable FinancialEvent.
    
    This enforces Constitution C1: Immutable ledger.
    """


class LedgerSequenceError(NFPError):
    """Raised when a sequence number gap or duplicate is detected."""


class DoubleEntryViolationError(NFPError):
    """Raised when DEBIT total != CREDIT total for a BusinessActivity."""
    def __init__(self, activity_id: str, debit: str, credit: str) -> None:
        super().__init__(
            f"Double-entry violation for activity {activity_id}: "
            f"DEBIT={debit} != CREDIT={credit}"
        )


# --- Domain Errors ---

class EvidenceRequiredError(NFPError):
    """Raised when a BusinessActivity has no evidence references."""


class InsufficientLotQuantityError(NFPError):
    """Raised when a SELL activity quantity exceeds available lot quantity."""
    def __init__(self, available: str, requested: str) -> None:
        super().__init__(
            f"Insufficient lot quantity: available={available}, requested={requested}"
        )


class ActivityTypeNotFoundError(NFPError):
    """Raised when an activity_type_code is not found in reference data."""
    def __init__(self, code: str) -> None:
        super().__init__(f"ActivityType not found: {code!r}")


class CurrencyNotFoundError(NFPError):
    """Raised when a currency code is not found in CurrencyRegistry."""
    def __init__(self, code: str) -> None:
        super().__init__(f"Currency not found: {code!r}")


class ExchangeRateNotFoundError(NFPError):
    """Raised when no exchange rate is available for the requested pair/date."""
    def __init__(self, from_ccy: str, to_ccy: str, on_date: str) -> None:
        super().__init__(f"No exchange rate for {from_ccy}/{to_ccy} on {on_date}")


class PriceNotAvailableError(NFPError):
    """Raised when a market price is not available for an asset/date."""
    def __init__(self, asset_id: str, on_date: str) -> None:
        super().__init__(f"No market price for asset {asset_id} on {on_date}")


class JurisdictionNotSupportedError(NFPError):
    """Raised when a TaxJurisdiction has no registered TaxRuleProvider."""
    def __init__(self, jurisdiction_code: str) -> None:
        super().__init__(f"No TaxRuleProvider registered for jurisdiction: {jurisdiction_code!r}")


class FileIntegrityError(NFPError):
    """Raised when an evidence file's SHA-256 hash does not match the stored hash."""
    def __init__(self, file_reference: str) -> None:
        super().__init__(f"File integrity check failed for: {file_reference!r}")


class LotNotFoundError(NFPError):
    """Raised when a Lot cannot be found by ID."""
    def __init__(self, lot_id: str) -> None:
        super().__init__(f"Lot not found: {lot_id!r}")
