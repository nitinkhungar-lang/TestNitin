"""Ledger repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import Ledger
from nfp.repositories.base import Repository

class LedgerRepository(Repository[Ledger, UUID], abc.ABC):
    """Repository interface for Ledger."""
    pass
