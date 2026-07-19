"""MarketPrice repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import MarketPrice
from nfp.repositories.base import Repository

class MarketPriceRepository(Repository[MarketPrice, UUID], abc.ABC):
    """Repository interface for MarketPrice."""
    pass
