"""Exchange Rate Provider ABC."""
from abc import ABC, abstractmethod
class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, base_currency: str, target_currency: str, date):
        pass
