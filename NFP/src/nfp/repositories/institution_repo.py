"""Institution repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import Institution
from nfp.repositories.base import Repository

class InstitutionRepository(Repository[Institution, UUID], abc.ABC):
    """Repository interface for Institution."""
    pass
