"""Manual Price Provider."""
from decimal import Decimal
from nfp.valuation.price_provider import PriceProvider, AssetValuation

class ManualPriceProvider(PriceProvider):
    def get_price(self, asset_id, date) -> AssetValuation:
        return AssetValuation(price=Decimal('100.0'))
