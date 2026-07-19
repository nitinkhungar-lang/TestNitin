"""FinancialAccount repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import FinancialAccount
from nfp.repositories.base import Repository

class FinancialAccountRepository(Repository[FinancialAccount, UUID], abc.ABC):
    """Repository interface for FinancialAccount."""
    pass
