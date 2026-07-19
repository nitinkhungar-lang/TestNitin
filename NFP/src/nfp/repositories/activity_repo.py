"""BusinessActivity repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import BusinessActivity
from nfp.repositories.base import Repository

class BusinessActivityRepository(Repository[BusinessActivity, UUID], abc.ABC):
    """Repository interface for BusinessActivity."""
    pass
