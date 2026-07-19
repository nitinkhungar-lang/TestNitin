"""Lot repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import Lot
from nfp.repositories.base import Repository

class LotRepository(Repository[Lot, UUID], abc.ABC):
    """Repository interface for Lot."""
    pass
