"""Identifier value object for NFP."""
from __future__ import annotations

from dataclasses import dataclass

_VALID_TYPES = frozenset({"ISIN", "SYMBOL", "PAN", "FOLIO_NO", "ACCOUNT_NO", "SEBI_REG", "IRDAI_REG"})


@dataclass(frozen=True)
class Identifier:
    """An immutable typed identifier for financial entities.

    Args:
        value: The identifier string value.
        id_type: The type of identifier. One of: ISIN, SYMBOL, PAN, FOLIO_NO, ACCOUNT_NO.

    Example::

        isin = Identifier('INE002A01018', 'ISIN')
        symbol = Identifier('RELIANCE', 'SYMBOL')
    """

    value: str
    id_type: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Identifier value cannot be empty")
        if self.id_type not in _VALID_TYPES:
            raise ValueError(f"Invalid identifier type: {self.id_type!r}. Valid: {_VALID_TYPES}")

    def __repr__(self) -> str:
        return f"Identifier({self.value!r}, {self.id_type!r})"
