"""CorporateAction repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import CorporateAction
from nfp.repositories.base import Repository

class CorporateActionRepository(Repository[CorporateAction, UUID], abc.ABC):
    """Repository interface for CorporateAction."""
    pass
