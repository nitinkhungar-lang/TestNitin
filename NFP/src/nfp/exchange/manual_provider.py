"""Manual Exchange Rate Provider."""
from nfp.exchange.provider import ExchangeRateProvider
class ManualExchangeRateProvider(ExchangeRateProvider):
    def get_rate(self, base_currency: str, target_currency: str, date):
        return 1.0
