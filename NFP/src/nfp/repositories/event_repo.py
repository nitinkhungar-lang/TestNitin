"""FinancialEvent repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import FinancialEvent
from nfp.repositories.base import Repository

class FinancialEventRepository(Repository[FinancialEvent, UUID], abc.ABC):
    """Repository interface for FinancialEvent."""
    pass
