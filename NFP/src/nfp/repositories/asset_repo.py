"""Asset repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import Asset
from nfp.repositories.base import Repository

class AssetRepository(Repository[Asset, UUID], abc.ABC):
    """Repository interface for Asset."""
    pass
