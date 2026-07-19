"""ExchangeRate repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.core.exchange_rate import ExchangeRate
from nfp.repositories.base import Repository

class ExchangeRateRepository(Repository[ExchangeRate, UUID], abc.ABC):
    """Repository interface for ExchangeRate."""
    pass
